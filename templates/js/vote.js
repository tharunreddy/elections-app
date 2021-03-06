$(document).ready(function () {
    function t(e) {
        $.ajax({
            dataType: "json",
            url: "/vote/" + e,
            type: "GET",
            success: function (t) {
                var n = [];
                $.each(t.results, function (e, t) {
                    n.push('<div class="positions-results-nom"><div class="left res-nom-name">' + e + '</div><div class="left bar"><div class="filled" style="width:' + t[0] + '%"></div></div><div class="left percentage">' + t[1] + ' votes</div><div class="clear"></div></div>')
                });
                $("#" + e).find(".positions-results-holder").html(n.join(""));
                var r = t.count;
                //if (e != "webadmin") {
                if (e != "socialchair" && e != "treasurer") {    
                    if (r != 0) {
                        var i = "times";
                        var s = "them";
                        if (r == 1) {
                            i = "time";
                            s = "it"
                        }
                        if (r == 3) {
                            $("#" + e).find(".vote-count").html("")
                        } else {
                            $("#" + e).find(".vote-count").html("You can change your vote only " + r + " " + i + " now. Use " + s + " wisely.")
                        }
                    } else {
                        $("#" + e).find(".vote-count").hide();
                        $("#" + e).find("form").hide();
                        $("#" + e).find(".ran-out").fadeIn();
                        $("#" + e).find(".positions-results-page").trigger("click");
                        $(".pos-nav").each(function () {
                            if ($(this).attr("to") == e) {
                                $(this).css({
                                    "background-color": "rgb(189, 54, 54)"
                                })
                            }
                        })
                    }
                } else {
                    if(e == "socialchair")
                    {
                        if (r < 3) {
                            $("#" + e).find(".vote-count").html("Well, you can't change your vote. Here's your new social chair!")
                        } else {
                            $("#" + e).find(".vote-count").html("")
                        }
                    }
                    else if(e == "treasurer")
                    {
                        if (r < 3) {
                            $("#" + e).find(".vote-count").html("Well, you can't change your vote. Here's your new treasurer!")
                        } else {
                            $("#" + e).find(".vote-count").html("")
                        }   
                    }

                }
            },
            error: function (e, t, n) {
                console.log(t)
            }
        })
    }

    function n() {
        t("chair");
        t("vicechair");
        t("treasurer");
        t("socialchair");
        t("operationschair");
        t("gapsaliason");
        t("communicationschair");
        t("webadmin");
        t("marketingchair")
    }
    var e = 3;
    $.stellar();
    $(".total-noms > .left").on("click keydown", function () {
        $(this).siblings("input[type=radio]").attr("checked", false);
        $(this).prev("input[type=radio]").attr("checked", true);
        $(this).siblings(".left").children("img").fadeTo(0, .5);
        $(this).children("img").fadeTo(0, 1)
    });
    $("input[type=submit]").click(function (e) {
        e.preventDefault();
        var t = $(this).parent().attr("id").substring(5);
        var n = "";
        $("input[name=" + t + "]").each(function () {
            if ($(this).attr("checked")) {
                n = $(this).val()
            }
        });
        if (n != "") {
            $.ajax({
                url: "/vote/" + t,
                type: "POST",
                data: t + "=" + n,
                success: function (e) {
                    $("#" + t).find(".positions-results-page").trigger("click");
                    $("#" + t).find(".results-refresh").trigger("click")
                }
            })
        } else {
            alert("Please select a candidate.")
        }
    });
    $(".positions-results > .results-refresh").click(function () {
        var e = $(this).parent().parent().parent().parent().parent().attr("id");
        t(e)
    });
    $(".positions-results-page").click(function () {
        $(this).parent().siblings(".positions-overflow").find(".positions-holder").stop().animate({
            top: "-350px"
        });
        $(this).siblings(".left").removeClass("nav-sel");
        $(this).addClass("nav-sel")
    });
    $(".positions-vote-page").click(function () {
        $(this).parent().siblings(".positions-overflow").find(".positions-holder").stop().animate({
            top: 0
        });
        $(this).siblings(".left").removeClass("nav-sel");
        $(this).addClass("nav-sel")
    });
    $(".pos-nav").click(function () {
        var e = $(this).attr("to");
      	if(e!='results') {
        	$("html,body").stop().animate({
            	scrollTop: $("#" + e).offset().top - 140
        	}, 1e3)
        }else{
          	$('.positions-results-page').trigger('click');
        }
    });
    n()
})