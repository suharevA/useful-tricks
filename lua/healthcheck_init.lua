-- /usr/local/openresty/nginx/conf/http/healthcheck_init.lua
-- Ansible managed: Healthcheck initialization

-- Переопределение ngx.log для подавления "шумных" таймерных ошибок
local original_log = ngx.log

ngx.log = function(level, ...)
    local msg = table.concat({...}, " ")

    if level == ngx.ERR and string.find(msg, "ngx.timer") then
        if string.find(msg, "Connection refused")
        or string.find(msg, "Connection reset by peer")
        or string.find(msg, "recv() failed")
        or string.find(msg, "connect() failed") then
            return
        end
    end

    original_log(level, ...)
end


ngx.log(ngx.NOTICE, "[healthcheck] initializing in worker 0")

-- Загрузка модуля healthcheck
local ok, hc = pcall(require, "resty.upstream.healthcheck")
if not ok then
    ngx.log(ngx.ERR, "[healthcheck] failed to load healthcheck module: " .. tostring(hc))
    return
end

-- Загрузка конфигурации healthcheck'ов
local ok2, checks = pcall(require, "healthchecks")
if not ok2 then
    ngx.log(ngx.ERR, "[healthcheck] failed to load healthchecks config: " .. tostring(checks))
    return
end

if not checks or type(checks) ~= "table" then
    ngx.log(ngx.ERR, "[healthcheck] healthchecks config is invalid")
    return
end

ngx.log(ngx.NOTICE, "[healthcheck] loaded " .. #checks .. " health checks")

-- Запуск healthcheck'ов
for _, check in ipairs(checks) do
    ngx.log(ngx.NOTICE, "[healthcheck] spawning check for upstream: " .. tostring(check.upstream))
    local ok, err = hc.spawn_checker(check)
    if not ok then
        ngx.log(ngx.ERR, "[healthcheck] failed to start for " .. tostring(check.upstream) .. ": " .. tostring(err))
    else
        ngx.log(ngx.NOTICE, "[healthcheck] started for upstream: " .. tostring(check.upstream))
    end
end