angular.module("AppConfig", [])
    .run(
        function($rootScope, $http, $interval, $location) {
            $rootScope.init_Config = function(){
                var url = 'init_config';
                $http.get(url).success(function (result) {
                    $rootScope.dataList = result;
                }).error(function () {

                })
            };

            // 弹出修改密码和注销
            $rootScope.showMenu = function () {
                if (!$rootScope.show_menu) {
                    $("#show_menu").show();
                    $rootScope.show_menu = true;
                } else {
                    $("#show_menu").hide();
                    $rootScope.show_menu = false;
                }
            };

            //注销
            $rootScope.logout = function () {
                // 清空 LocalSotrge
                localStorage.removeItem('two_userid');
                localStorage.removeItem('two_user_name');
                localStorage.removeItem('two_user_password');
                localStorage.removeItem('two_is_admin');
                localStorage.removeItem('two_true_name');
                localStorage.removeItem('two_see_setting');
                window.open('go_login', '_self')
            };

            //打开修改密码弹出框
            $rootScope.showPassword = function () {
                $("#show_menu").hide();
                $rootScope.show_menu = false;
                $('#passwordModel').modal();
                $("#oldpassword").val("");
                $("#newpassword").val("");
                $("#r_newpassword").val("");
            };

            //生成csrftoken
            function getCookie(name) {
                var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
                if (arr = document.cookie.match(reg))
                    return decodeURI(arr[2]);
                else
                    return null;
            }

            //修改密码
            $rootScope.savePassword = function() {
                if (!$("#oldpassword").val() || $("#oldpassword").val() == "") {
                    toastr.warning("原密码不能为空");
                    return;
                }
                if (!$("#newpassword").val() || $("#newpassword").val() == "") {
                    toastr.warning("新密码不能为空");
                    return;
                }
                if (!$("#r_newpassword").val() || $("#r_newpassword").val() == "") {
                    toastr.warning("请再次输入新密码");
                    return;
                }
                if ($("#newpassword").val() != $("#r_newpassword").val()) {
                    toastr.warning("新密码两次不一致");
                    return;
                }
                if ($("#oldpassword").val() == $("#newpassword").val()) {
                    toastr.warning("新密码不能与旧密码一致");
                    return;
                }
                $.ajax({
                    headers: {"X-CSRFToken": getCookie("csrftoken")},
                    url: "updatePassword",
                    type: 'POST', //GET、PUT、DELETE
                    async: false,    //是否异步
                    timeout: 10000,    //超时时间
                    data: {
                        "user_id": $rootScope.userid,
                        "oldpassword": $("#oldpassword").val(),
                        "newpassword": $("#newpassword").val(),
                    },
                    dataType: 'json',    //返回的数据格式：json/xml/html/script/jsonp/text
                    beforeSend: function (xhr) {
                        // 发送前处理
                    },
                    success: function (data, textStatus, jqXHR) {
                        if (data[0]['code'] == "0") {
                            toastr.success("修改成功");
                            $('#passwordModel').modal('hide');
                        } else {
                            toastr.error(data[0]['msg']);
                        }
                    },
                    error: function (xhr, textStatus) {
                        // 调用时，发生错误
                        toastr.warning(textStatus);
                    },
                    complete: function () {
                        // 交互后处理
                    }
                })
            };
            $rootScope.close_update = function(){
                $("#update").modal('hide');
                location.reload();
            };
            $rootScope.init_Config();
        });

$(function () {
    if(localStorage.getItem('two_userid') == null){
        window.open('go_login', '_self'); //没找到apptoken就返回登陆界面
    }else{
        if(localStorage.getItem('two_is_admin') == 't'){
            $('#go_setting').show();
            $('#go_user').show();
        }else{
            if(localStorage.getItem('two_see_setting') == '0'){
                $('#go_setting').hide();
                $('#go_user').hide();
            }else{
                $('#go_setting').show();
                $('#go_user').hide();
            }
        }
    }
});