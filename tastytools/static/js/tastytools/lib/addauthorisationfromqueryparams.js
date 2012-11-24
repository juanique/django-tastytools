/**
 * Forward any query params in the browser window to any requests made to the api.
 *
 * So will work with APIAuthentication in tastypie
 */
$.ajaxSetup({ beforeSend:function (xhr, settings) {
    var user = "example";
    var key = 1234;
    if (user && key) {
        var token = "ApiKey " + user + ":" + key;
        console.log("Authorisation " + token);
        xhr.setRequestHeader('Authorization', token);
    }
}});