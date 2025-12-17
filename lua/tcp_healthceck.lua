return {
    {
        name = "test-gost-openresty_mos_ru_gost",
        servers = {
            { host = "10.x.x.x", port = 9443 },
            -- { host = "10.x.x.y", port = 9443, backup = true },
        },
        interval = 2,
        timeout = 1000,
        fall = 3,
        rise = 2,
        down_log_interval = 60,
        use_proxy_protocol = false,  -- просто TCP connect
    },
}

init_worker_by_lua_block {
    local tcp_upstreams = dofile("/usr/local/openresty/nginx/conf/tcp_healthchecks.lua")
    local upstream_states = {}

    -- Простой TCP healthcheck - только проверка connect
    local function tcp_healthcheck(config)
        local upstream_name = config.name
        local host = config.host
        local port = config.port
        local timeout = config.timeout or 1000
        local fall = config.fall or 2
        local rise = config.rise or 1
        local down_log_interval = config.down_log_interval or 60
        local backup = config.backup or false

        local key = upstream_name .. "_" .. host .. ":" .. port

        if not upstream_states[key] then
            upstream_states[key] = {
                is_up = true,
                consecutive_failures = 0,
                consecutive_successes = 0,
                last_down_log = 0,
                backup = backup,
            }
        end

        local state = upstream_states[key]
        local sock = ngx.socket.tcp()
        sock:settimeout(timeout)
        local backup_label = backup and " [BACKUP]" or ""

        local ok, err = sock:connect(host, port)
        sock:close()

        if not ok then
            state.consecutive_failures = state.consecutive_failures + 1
            state.consecutive_successes = 0

            if state.is_up and state.consecutive_failures >= fall then
                state.is_up = false
                state.last_down_log = ngx.now()
                ngx.log(ngx.ERR,
                    "TCP upstream " .. upstream_name .. backup_label ..
                    ": " .. host .. ":" .. port .. " is DOWN (" .. tostring(err) .. ")"
                )
            elseif not state.is_up then
                local now = ngx.now()
                if (now - state.last_down_log) >= down_log_interval then
                    state.last_down_log = now
                    ngx.log(ngx.WARN,
                        "TCP upstream " .. upstream_name .. backup_label ..
                        ": " .. host .. ":" .. port .. " still DOWN"
                    )
                end
            end
            return false
        end

        state.consecutive_successes = state.consecutive_successes + 1
        state.consecutive_failures = 0

        if not state.is_up and state.consecutive_successes >= rise then
            state.is_up = true
            ngx.log(ngx.NOTICE,
                "TCP upstream " .. upstream_name .. backup_label ..
                ": " .. host .. ":" .. port .. " is back UP"
            )
        end

        return true
    end

    -- Планировщик
    local function schedule_tcp_checks()
        for _, upstream in ipairs(tcp_upstreams) do
            for _, srv in ipairs(upstream.servers) do
                local ok, err = ngx.timer.every(upstream.interval, function()
                    tcp_healthcheck({
                        name = upstream.name,
                        host = srv.host,
                        port = srv.port,
                        timeout = upstream.timeout,
                        fall = upstream.fall,
                        rise = upstream.rise,
                        down_log_interval = upstream.down_log_interval,
                        backup = srv.backup or false,
                    })
                end)

                if ok then
                    ngx.log(ngx.NOTICE,
                        "[healthcheck] TCP check started: " .. upstream.name ..
                        " (" .. srv.host .. ":" .. srv.port .. ")"
                    )
                end
            end
        end
    end

    schedule_tcp_checks()

    _G.get_upstream_states = function()
        return upstream_states
    end
}