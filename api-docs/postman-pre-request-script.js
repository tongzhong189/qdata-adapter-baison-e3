// Postman Pre-request Script
// 百胜E3 正确签名算法（参考 PHP BaisonSDK）
// 复制到 Postman 请求的 Pre-request Script 标签页中
//
// 使用前请在 Postman 环境变量中设置：
//   - baison_app_key    : 你的 AppKey
//   - baison_app_secret : 你的 AppSecret
//   - baison_base_url   : 你的 base_url（可选）
//   - baison_api        : API 接口名称（可选，默认 e3oms.base.sd.get）
//   - baison_data       : 请求 data JSON 字符串（可选，默认 {"pageNo":1,"pageSize":5}）

var APP_KEY = pm.environment.get("baison_app_key") || "YOUR_APP_KEY";
var APP_SECRET = pm.environment.get("baison_app_secret") || "YOUR_APP_SECRET";

if (APP_KEY === "YOUR_APP_KEY" || APP_SECRET === "YOUR_APP_SECRET") {
    console.error("请在 Postman 环境变量中设置 baison_app_key 和 baison_app_secret");
}

// 获取当前时间戳 (yyyyMMddHHmmss)
function getRequestTime() {
    var now = new Date();
    var pad = function(n) { return n < 10 ? '0' + n : n; };
    return '' + now.getFullYear() + pad(now.getMonth() + 1) + pad(now.getDate()) +
           pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
}

// MD5 加密（小写）
function md5(string) {
    return CryptoJS.MD5(string).toString();
}

// 从环境变量读取 API 名称和请求数据
var api = pm.environment.get("baison_api") || "e3oms.base.sd.get";
var dataValue = pm.environment.get("baison_data") || '{"pageNo":1,"pageSize":5}';

// 构建签名参数（包含 secret）
var signParams = {
    key: APP_KEY,
    requestTime: getRequestTime(),
    secret: APP_SECRET,
    version: "3.0",
    serviceType: api
};

// http_build_query 编码 + &data= + 原始 JSON
var sortedKeys = Object.keys(signParams).sort();
var queryStr = "";
sortedKeys.forEach(function(key, index) {
    if (index > 0) queryStr += "&";
    queryStr += key + "=" + signParams[key];
});
queryStr += "&data=" + dataValue;

// MD5 小写签名
var sign = md5(queryStr);

// 设置到查询参数（注意：不包含 secret）
pm.request.url.addQueryParams([
    { key: "app_act", value: "api/ec" },
    { key: "app_mode", value: "func" },
    { key: "serviceType", value: api },
    { key: "key", value: APP_KEY },
    { key: "requestTime", value: signParams.requestTime },
    { key: "version", value: "3.0" },
    { key: "data", value: dataValue },
    { key: "sign", value: sign }
]);

console.log("API:", api);
console.log("RequestTime:", signParams.requestTime);
console.log("Sign String:", queryStr);
console.log("Sign Result:", sign);
