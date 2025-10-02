init_worker_by_lua_block {
    local tcp_upstreams = dofile("/usr/local/openresty/nginx/conf/tcp_healthchecks.lua")
    local upstream_states = {}

    -- Функция создания PROXY protocol v1 заголовка
    local function create_proxy_header(src_ip, dest_ip, src_port, dest_port, protocol)
        protocol = protocol or "TCP4"
        src_ip = src_ip or "127.0.0.1"
        dest_ip = dest_ip or "127.0.0.1"
        src_port = src_port or 12345
        dest_port = dest_port or 80

        return string.format("PROXY %s %s %s %d %d\r\n",
                           protocol, src_ip, dest_ip, src_port, dest_port)
    end

    -- TCP healthcheck
    local function tcp_healthcheck(config)
        local upstream_name = config.name
        local host = config.host
        local port = config.port
        local timeout = config.timeout or 1000
        local fall = config.fall or 2
        local rise = config.rise or 1
        local down_log_interval = config.down_log_interval or 60
        local use_proxy_protocol = config.use_proxy_protocol or false
        local proxy_src_ip = config.proxy_src_ip
        local proxy_dest_ip = config.proxy_dest_ip
        local proxy_src_port = config.proxy_src_port
        local proxy_dest_port = config.proxy_dest_port
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
        if not ok then
            state.consecutive_failures = state.consecutive_failures + 1
            state.consecutive_successes = 0

            if state.is_up and state.consecutive_failures >= fall then
                state.is_up = false
                state.last_down_log = ngx.now()
                ngx.log(ngx.ERR,
                    "TCP upstream " .. upstream_name .. backup_label ..
                    ": server " .. host .. ":" .. port .. " is DOWN (connect failed: " .. tostring(err) .. ")"
                )
            else
                local now = ngx.now()
                if not state.is_up and (now - state.last_down_log) >= down_log_interval then
                    state.last_down_log = now
                    ngx.log(ngx.WARN,
                        "TCP upstream " .. upstream_name .. backup_label ..
                        ": server " .. host .. ":" .. port ..
                        " still DOWN (fails=" .. state.consecutive_failures .. ", error: " .. tostring(err) .. ")"
                    )
                end
            end

            sock:close()
            return false
        end

        -- Если используется PROXY protocol, отправляем заголовок
        if use_proxy_protocol then
            local proxy_header = create_proxy_header(
                proxy_src_ip,
                proxy_dest_ip or host,
                proxy_src_port,
                proxy_dest_port or port
            )

            local bytes, send_err = sock:send(proxy_header)
            if not bytes then
                state.consecutive_failures = state.consecutive_failures + 1
                state.consecutive_successes = 0

                if state.is_up and state.consecutive_failures >= fall then
                    state.is_up = false
                    state.last_down_log = ngx.now()
                    ngx.log(ngx.ERR,
                        "TCP upstream " .. upstream_name .. backup_label ..
                        ": server " .. host .. ":" .. port .. " is DOWN (PROXY protocol send failed: " .. tostring(send_err) .. ")"
                    )
                end

                sock:close()
                return false
            end
        end

        sock:close()

        state.consecutive_successes = state.consecutive_successes + 1
        state.consecutive_failures = 0

        if not state.is_up and state.consecutive_successes >= rise then
            state.is_up = true
            local proxy_info = use_proxy_protocol and " (with PROXY protocol)" or ""
            ngx.log(ngx.NOTICE,
                "TCP upstream " .. upstream_name .. backup_label ..
                ": server " .. host .. ":" .. port .. " is back UP" .. proxy_info
            )
        elseif state.is_up then
            if state.consecutive_successes % 10 == 0 then
                local proxy_info = use_proxy_protocol and " (PROXY)" or ""
                ngx.log(ngx.NOTICE,
                    "TCP upstream " .. upstream_name .. backup_label ..
                    ": server " .. host .. ":" .. port .. " is UP" .. proxy_info
                )
            end
        end

        return true
    end

    -- Планировщик TCP healthchecks
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
                        use_proxy_protocol = upstream.use_proxy_protocol,
                        proxy_src_ip = upstream.proxy_src_ip,
                        proxy_dest_ip = upstream.proxy_dest_ip,
                        proxy_src_port = upstream.proxy_src_port,
                        proxy_dest_port = upstream.proxy_dest_port,
                        backup = srv.backup or false,
                    })
                end)

                if not ok then
                    ngx.log(ngx.ERR,
                        "Failed to create TCP healthcheck timer for "
                        .. upstream.name .. " (" .. srv.host .. ":" .. srv.port .. "): " .. tostring(err)
                    )
                else
                    local proxy_info = upstream.use_proxy_protocol and " with PROXY protocol" or ""
                    ngx.log(ngx.NOTICE,
                        "[healthcheck] TCP timer created for " .. upstream.name ..
                        " (" .. srv.host .. ":" .. srv.port .. proxy_info ..
                        ") - timeout:" .. upstream.timeout .. "ms, fall:" .. upstream.fall ..
                        ", rise:" .. upstream.rise ..
                        ", interval:" .. upstream.interval .. "s"
                    )
                end
            end
        end
    end

    -- Подавление шумных ошибок таймеров
    local original_log = ngx.log
    ngx.log = function(level, ...)
        local msg = table.concat({...}, " ")
        if level == ngx.ERR and string.find(msg, "ngx.timer") then
            if string.find(msg, "Connection refused")
            or string.find(msg, "Connection reset by peer")
            or string.find(msg, "recv() failed")
            or string.find(msg, "connect() failed")
            or string.find(msg, "timeout") then
                return
            end
        end
        original_log(level, ...)
    end

    -- Запускаем TCP healthchecks
    schedule_tcp_checks()

    -- API для /tcp_status
    _G.get_upstream_states = function()
        return upstream_states
    end
}
lua_shared_dict upstream_status 10m;

server {
    listen 0.0.0.0:8989;

    location = /tcp_status {
        default_type application/json;
        content_by_lua_block {
            local cjson = require "cjson"
            local states = {}
            if _G.get_upstream_states then
                local worker_states = _G.get_upstream_states()
                for key, state in pairs(worker_states) do
                    states[key] = {
                        is_up = state.is_up,
                        consecutive_failures = state.consecutive_failures,
                        consecutive_successes = state.consecutive_successes,
                        last_check = ngx.now()
                    }
                end
            end
            ngx.say(cjson.encode({
                worker_id = ngx.worker.id(),
                timestamp = ngx.now(),
                upstreams = states
            }))
        }
    }

    location = /healthcheck_status {
        default_type text/plain;
        content_by_lua_block {
            ngx.say("# HELP nginx_upstream_tcp_up Upstream server is up (1) or down (0)")
            ngx.say("# TYPE nginx_upstream_tcp_up gauge")
            ngx.say("# HELP nginx_upstream_tcp_failures Total consecutive failures")
            ngx.say("# TYPE nginx_upstream_tcp_failures counter")
            ngx.say("")

            if _G.get_upstream_states then
                local states = _G.get_upstream_states()
                for key, state in pairs(states) do
                    local upstream_name, host, port = key:match("^(.-)_(.+):(%d+)$")
                    if upstream_name and host and port then
                        local backup_label = state.backup and "backup" or "primary"
                        local labels = string.format('upstream="%s",server="%s",port="%s",role="%s"',
                            upstream_name, host, port, backup_label)
                        ngx.say(string.format('nginx_upstream_tcp_up{%s} %d',
                               labels, state.is_up and 1 or 0))
                        ngx.say(string.format('nginx_upstream_tcp_failures{%s} %d',
                               labels, state.consecutive_failures))
                    end
                end
            end
        }
    }
}
