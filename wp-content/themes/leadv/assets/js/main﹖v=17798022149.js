(function ($) {
    "use strict";

    function initMobileMenu() {
        var $toggle = $(".mobile-menu-toggle");
        var $nav = $("#mobile-nav");
        var $body = $("body");
        var $label = $toggle.find(".mobile-menu-toggle-label");
        var closedLabel = $toggle.attr("data-label-closed") || "Menu";
        var openLabel = $toggle.attr("data-label-open") || "Fechar";
        var $submenuParents = $nav.find(".menu-item-has-children");
        var $submenuTriggers = $submenuParents.children("a");
        var $submenus = $submenuParents.children("ul, .dropdown-menu");

        if (!$toggle.length || !$nav.length) {
            return;
        }

        $submenus.attr("aria-hidden", "true").hide();
        $submenuTriggers.attr("aria-haspopup", "true").attr("aria-expanded", "false");

        function collapseSubmenus() {
            $submenuParents.removeClass("is-open");
            $submenuTriggers.attr("aria-expanded", "false");
            $submenus.stop(true, true).slideUp(0).attr("aria-hidden", "true");
        }

        function closeMenu() {
            $toggle.removeClass("is-active").attr("aria-expanded", "false");
            $nav.removeClass("is-open").attr("aria-hidden", "true");
            $body.removeClass("mobile-menu-open");
            if ($label.length) {
                $label.text(closedLabel);
            }
            collapseSubmenus();
        }

        function openMenu() {
            $toggle.addClass("is-active").attr("aria-expanded", "true");
            $nav.addClass("is-open").attr("aria-hidden", "false");
            $body.addClass("mobile-menu-open");
            if ($label.length) {
                $label.text(openLabel);
            }
        }

        closeMenu();

        // Função para toggle do menu (reutilizável para click e touch)
        function handleToggle(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            if ($toggle.hasClass("is-active")) {
                closeMenu();
            } else {
                openMenu();
            }
        }

        // Suporte para eventos de toque (mobile) e click (desktop)
        $toggle.off(".mobileMenu");
        
        // Adicionar eventos de toque para dispositivos móveis
        $toggle.on("touchstart.mobileMenu", function (event) {
            // Prevenir o click duplo em dispositivos que disparam ambos
            var $this = $(this);
            if (!$this.data('touchHandled')) {
                $this.data('touchHandled', true);
                handleToggle(event);
                setTimeout(function() {
                    $this.data('touchHandled', false);
                }, 300);
            }
        });

        // Manter suporte a click para compatibilidade
        $toggle.on("click.mobileMenu", function (event) {
            // Ignorar click se já foi tratado por touchstart
            if (!$(this).data('touchHandled')) {
                handleToggle(event);
            }
        });

        $nav.off(".mobileMenu").on("click.mobileMenu", function (event) {
            event.stopPropagation();
        });

        $nav.find("a").off(".mobileMenuLink").on("click.mobileMenuLink", function () {
            closeMenu();
        });

        $(document).off(".mobileMenu").on("click.mobileMenu", function () {
            closeMenu();
        });

        $submenuTriggers.off(".mobileMenuSub").on("click.mobileMenuSub", function (event) {
            if (window.innerWidth > 991) {
                return;
            }

            var $link = $(this);
            var $item = $link.parent("li");
            var $submenu = $item.children("ul, .dropdown-menu");

            if (!$submenu.length) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();

            if ($item.hasClass("is-open")) {
                $item.removeClass("is-open");
                $submenu.stop(true, true).slideUp(200).attr("aria-hidden", "true");
                $link.attr("aria-expanded", "false");
            } else {
                $item.addClass("is-open");
                $submenu.stop(true, true).slideDown(200).attr("aria-hidden", "false");
                $link.attr("aria-expanded", "true");
            }
        });

        $(window).off(".mobileMenu").on("resize.mobileMenu", function () {
            if (window.innerWidth > 991) {
                closeMenu();
                $submenus.css("display", "");
            }
        });
    }

    function bindUI() {
        $(window).on("scroll", function () {
            if ($(this).scrollTop() > 120) {
                $(".navbar-area").addClass("is-sticky");
            } else {
                $(".navbar-area").removeClass("is-sticky");
            }
        });

        $(".default-btn").on("mouseenter", function (event) {
            var offset = $(this).offset(),
                relX = event.pageX - offset.left,
                relY = event.pageY - offset.top;
            $(this).find("span").css({ top: relY, left: relX });
        }).on("mouseout", function (event) {
            var offset = $(this).offset(),
                relX = event.pageX - offset.left,
                relY = event.pageY - offset.top;
            $(this).find("span").css({ top: relY, left: relX });
        });

        $(".close-btn").on("click", function () {
            $(".search-overlay").fadeOut();
            $(".search-btn").show();
            $(".close-btn").removeClass("active");
        });

        $(".search-btn").on("click", function () {
            $(this).hide();
            $(".search-overlay").fadeIn();
            $(".close-btn").addClass("active");
        });

        (function (t) {
            t(".tab ul.tabs-list").addClass("active").find("> li:eq(0)").addClass("current");
            t(".tab ul.tabs-list li").on("click", function (n) {
                var e = t(this).closest(".tab"),
                    s = t(this).closest("li").index();
                e.find("ul.tabs-list > li").removeClass("current");
                t(this).closest("li").addClass("current");
                e.find(".tab_content").find("div.tabs_item").not("div.tabs_item:eq(" + s + ")").slideUp();
                e.find(".tab_content").find("div.tabs_item:eq(" + s + ")").slideDown();
                n.preventDefault();
            });
        }(jQuery));

        $(".accordion").find(".accordion-title").on("click", function () {
            $(this).toggleClass("active");
            $(this).next().slideToggle("fast");
            $(".accordion-content").not($(this).next()).slideUp("fast");
            $(".accordion-title").not($(this)).removeClass("active");
        });

        $(window).on("scroll", function () {
            var n = $(window).scrollTop();
            if (n > 600) {
                $(".go-top").addClass("active");
            } else {
                $(".go-top").removeClass("active");
            }
        });

        $(".go-top").on("click", function () {
            $("html, body").animate({ scrollTop: "0" }, 0);
        });
    }

    var booted = false;

    function stripUnsupportedProperties() {
        try {
            document.querySelectorAll("[style*=\"contain-intrinsic-size\"], [data-style*=\"contain-intrinsic-size\"]").forEach(function (el) {
                var inlineStyle = el.getAttribute("style");
                var dataStyle = el.getAttribute("data-style");
                function cleanStyle(styleString) {
                    if (!styleString || styleString.indexOf("contain-intrinsic-size") === -1) {
                        return styleString;
                    }
                    var cleaned = styleString.replace(/contain-intrinsic-size\\s*:[^;]+;?/gi, "").replace(/;;+/g, ";").trim();
                    if (cleaned.endsWith(";")) {
                        cleaned = cleaned.slice(0, -1);
                    }
                    return cleaned;
                }
                var updatedInline = cleanStyle(inlineStyle);
                if (updatedInline !== inlineStyle) {
                    if (updatedInline) {
                        el.setAttribute("style", updatedInline);
                    } else {
                        el.removeAttribute("style");
                    }
                }
                var updatedData = cleanStyle(dataStyle);
                if (updatedData !== dataStyle) {
                    if (updatedData) {
                        el.setAttribute("data-style", updatedData);
                    } else {
                        el.removeAttribute("data-style");
                    }
                }
            });
        } catch (error) {
            if (window.console && console.warn) {
                console.warn("Falha ao remover contain-intrinsic-size:", error);
            }
        }
    }

    function boot() {
        if (booted) {
            return;
        }
        booted = true;
        bindUI();
        initMobileMenu();
        stripUnsupportedProperties();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    window.addEventListener("rocket-DOMContentLoaded", initMobileMenu);
    window.addEventListener("rocket-allScriptsLoaded", initMobileMenu);
    window.addEventListener("rocket-DOMContentLoaded", stripUnsupportedProperties);
    window.addEventListener("rocket-allScriptsLoaded", stripUnsupportedProperties);
    window.addEventListener("load", stripUnsupportedProperties);
})(jQuery);
/*! lazysizes - v5.2.0 */
!function(a,b){var c=b(a,a.document,Date);a.lazySizes=c,"object"==typeof module&&module.exports&&(module.exports=c)}("undefined"!=typeof window?window:{},function(a,b,c){"use strict";var d,e;if(function(){var b,c={lazyClass:"lazyload",loadedClass:"lazyloaded",loadingClass:"lazyloading",preloadClass:"lazypreload",errorClass:"lazyerror",autosizesClass:"lazyautosizes",srcAttr:"data-src",srcsetAttr:"data-srcset",sizesAttr:"data-sizes",minSize:40,customMedia:{},init:!0,expFactor:1.5,hFac:.8,loadMode:2,loadHidden:!0,ricTimeout:0,throttleDelay:125};e=a.lazySizesConfig||a.lazysizesConfig||{};for(b in c)b in e||(e[b]=c[b])}(),!b||!b.getElementsByClassName)return{init:function(){},cfg:e,noSupport:!0};var f=b.documentElement,g=a.HTMLPictureElement,h="addEventListener",i="getAttribute",j=a[h].bind(a),k=a.setTimeout,l=a.requestAnimationFrame||k,m=a.requestIdleCallback,n=/^picture$/i,o=["load","error","lazyincluded","_lazyloaded"],p={},q=Array.prototype.forEach,r=function(a,b){return p[b]||(p[b]=new RegExp("(\\s|^)"+b+"(\\s|$)")),p[b].test(a[i]("class")||"")&&p[b]},s=function(a,b){r(a,b)||a.setAttribute("class",(a[i]("class")||"").trim()+" "+b)},t=function(a,b){var c;(c=r(a,b))&&a.setAttribute("class",(a[i]("class")||"").replace(c," "))},u=function(a,b,c){var d=c?h:"removeEventListener";c&&u(a,b),o.forEach(function(c){a[d](c,b)})},v=function(a,c,e,f,g){var h=b.createEvent("Event");return e||(e={}),e.instance=d,h.initEvent(c,!f,!g),h.detail=e,a.dispatchEvent(h),h},w=function(b,c){var d;!g&&(d=a.picturefill||e.pf)?(c&&c.src&&!b[i]("srcset")&&b.setAttribute("srcset",c.src),d({reevaluate:!0,elements:[b]})):c&&c.src&&(b.src=c.src)},x=function(a,b){return(getComputedStyle(a,null)||{})[b]},y=function(a,b,c){for(c=c||a.offsetWidth;c<e.minSize&&b&&!a._lazysizesWidth;)c=b.offsetWidth,b=b.parentNode;return c},z=function(){var a,c,d=[],e=[],f=d,g=function(){var b=f;for(f=d.length?e:d,a=!0,c=!1;b.length;)b.shift()();a=!1},h=function(d,e){a&&!e?d.apply(this,arguments):(f.push(d),c||(c=!0,(b.hidden?k:l)(g)))};return h._lsFlush=g,h}(),A=function(a,b){return b?function(){z(a)}:function(){var b=this,c=arguments;z(function(){a.apply(b,c)})}},B=function(a){var b,d=0,f=e.throttleDelay,g=e.ricTimeout,h=function(){b=!1,d=c.now(),a()},i=m&&g>49?function(){m(h,{timeout:g}),g!==e.ricTimeout&&(g=e.ricTimeout)}:A(function(){k(h)},!0);return function(a){var e;(a=!0===a)&&(g=33),b||(b=!0,e=f-(c.now()-d),e<0&&(e=0),a||e<9?i():k(i,e))}},C=function(a){var b,d,e=99,f=function(){b=null,a()},g=function(){var a=c.now()-d;a<e?k(g,e-a):(m||f)(f)};return function(){d=c.now(),b||(b=k(g,e))}},D=function(){var g,m,o,p,y,D,F,G,H,I,J,K,L=/^img$/i,M=/^iframe$/i,N="onscroll"in a&&!/(gle|ing)bot/.test(navigator.userAgent),O=0,P=0,Q=0,R=-1,S=function(a){Q--,(!a||Q<0||!a.target)&&(Q=0)},T=function(a){return null==K&&(K="hidden"==x(b.body,"visibility")),K||!("hidden"==x(a.parentNode,"visibility")&&"hidden"==x(a,"visibility"))},U=function(a,c){var d,e=a,g=T(a);for(G-=c,J+=c,H-=c,I+=c;g&&(e=e.offsetParent)&&e!=b.body&&e!=f;)(g=(x(e,"opacity")||1)>0)&&"visible"!=x(e,"overflow")&&(d=e.getBoundingClientRect(),g=I>d.left&&H<d.right&&J>d.top-1&&G<d.bottom+1);return g},V=function(){var a,c,h,j,k,l,n,o,q,r,s,t,u=d.elements;if((p=e.loadMode)&&Q<8&&(a=u.length)){for(c=0,R++;c<a;c++)if(u[c]&&!u[c]._lazyRace)if(!N||d.prematureUnveil&&d.prematureUnveil(u[c]))ba(u[c]);else if((o=u[c][i]("data-expand"))&&(l=1*o)||(l=P),r||(r=!e.expand||e.expand<1?f.clientHeight>500&&f.clientWidth>500?500:370:e.expand,d._defEx=r,s=r*e.expFactor,t=e.hFac,K=null,P<s&&Q<1&&R>2&&p>2&&!b.hidden?(P=s,R=0):P=p>1&&R>1&&Q<6?r:O),q!==l&&(D=innerWidth+l*t,F=innerHeight+l,n=-1*l,q=l),h=u[c].getBoundingClientRect(),(J=h.bottom)>=n&&(G=h.top)<=F&&(I=h.right)>=n*t&&(H=h.left)<=D&&(J||I||H||G)&&(e.loadHidden||T(u[c]))&&(m&&Q<3&&!o&&(p<3||R<4)||U(u[c],l))){if(ba(u[c]),k=!0,Q>9)break}else!k&&m&&!j&&Q<4&&R<4&&p>2&&(g[0]||e.preloadAfterLoad)&&(g[0]||!o&&(J||I||H||G||"auto"!=u[c][i](e.sizesAttr)))&&(j=g[0]||u[c]);j&&!k&&ba(j)}},W=B(V),X=function(a){var b=a.target;if(b._lazyCache)return void delete b._lazyCache;S(a),s(b,e.loadedClass),t(b,e.loadingClass),u(b,Z),v(b,"lazyloaded")},Y=A(X),Z=function(a){Y({target:a.target})},$=function(a,b){try{a.contentWindow.location.replace(b)}catch(c){a.src=b}},_=function(a){var b,c=a[i](e.srcsetAttr);(b=e.customMedia[a[i]("data-media")||a[i]("media")])&&a.setAttribute("media",b),c&&a.setAttribute("srcset",c)},aa=A(function(a,b,c,d,f){var g,h,j,l,m,p;(m=v(a,"lazybeforeunveil",b)).defaultPrevented||(d&&(c?s(a,e.autosizesClass):a.setAttribute("sizes",d)),h=a[i](e.srcsetAttr),g=a[i](e.srcAttr),f&&(j=a.parentNode,l=j&&n.test(j.nodeName||"")),p=b.firesLoad||"src"in a&&(h||g||l),m={target:a},s(a,e.loadingClass),p&&(clearTimeout(o),o=k(S,2500),u(a,Z,!0)),l&&q.call(j.getElementsByTagName("source"),_),h?a.setAttribute("srcset",h):g&&!l&&(M.test(a.nodeName)?$(a,g):a.src=g),f&&(h||l)&&w(a,{src:g})),a._lazyRace&&delete a._lazyRace,t(a,e.lazyClass),z(function(){var b=a.complete&&a.naturalWidth>1;p&&!b||(b&&s(a,"ls-is-cached"),X(m),a._lazyCache=!0,k(function(){"_lazyCache"in a&&delete a._lazyCache},9)),"lazy"==a.loading&&Q--},!0)}),ba=function(a){if(!a._lazyRace){var b,c=L.test(a.nodeName),d=c&&(a[i](e.sizesAttr)||a[i]("sizes")),f="auto"==d;(!f&&m||!c||!a[i]("src")&&!a.srcset||a.complete||r(a,e.errorClass)||!r(a,e.lazyClass))&&(b=v(a,"lazyunveilread").detail,f&&E.updateElem(a,!0,a.offsetWidth),a._lazyRace=!0,Q++,aa(a,b,f,d,c))}},ca=C(function(){e.loadMode=3,W()}),da=function(){3==e.loadMode&&(e.loadMode=2),ca()},ea=function(){if(!m){if(c.now()-y<999)return void k(ea,999);m=!0,e.loadMode=3,W(),j("scroll",da,!0)}};return{_:function(){y=c.now(),d.elements=b.getElementsByClassName(e.lazyClass),g=b.getElementsByClassName(e.lazyClass+" "+e.preloadClass),j("scroll",W,!0),j("resize",W,!0),j("pageshow",function(a){if(a.persisted){var c=b.querySelectorAll("."+e.loadingClass);c.length&&c.forEach&&l(function(){c.forEach(function(a){a.complete&&ba(a)})})}}),a.MutationObserver?new MutationObserver(W).observe(f,{childList:!0,subtree:!0,attributes:!0}):(f[h]("DOMNodeInserted",W,!0),f[h]("DOMAttrModified",W,!0),setInterval(W,999)),j("hashchange",W,!0),["focus","mouseover","click","load","transitionend","animationend"].forEach(function(a){b[h](a,W,!0)}),/d$|^c/.test(b.readyState)?ea():(j("load",ea),b[h]("DOMContentLoaded",W),k(ea,2e4)),d.elements.length?(V(),z._lsFlush()):W()},checkElems:W,unveil:ba,_aLSL:da}}(),E=function(){var a,c=A(function(a,b,c,d){var e,f,g;if(a._lazysizesWidth=d,d+="px",a.setAttribute("sizes",d),n.test(b.nodeName||""))for(e=b.getElementsByTagName("source"),f=0,g=e.length;f<g;f++)e[f].setAttribute("sizes",d);c.detail.dataAttr||w(a,c.detail)}),d=function(a,b,d){var e,f=a.parentNode;f&&(d=y(a,f,d),e=v(a,"lazybeforesizes",{width:d,dataAttr:!!b}),e.defaultPrevented||(d=e.detail.width)&&d!==a._lazysizesWidth&&c(a,f,e,d))},f=function(){var b,c=a.length;if(c)for(b=0;b<c;b++)d(a[b])},g=C(f);return{_:function(){a=b.getElementsByClassName(e.autosizesClass),j("resize",g)},checkElems:g,updateElem:d}}(),F=function(){!F.i&&b.getElementsByClassName&&(F.i=!0,E._(),D._())};return k(function(){e.init&&F()}),d={cfg:e,autoSizer:E,loader:D,init:F,uP:w,aC:s,rC:t,hC:r,fire:v,gW:y,rAF:z}});
/* PRIVACY POLICY */
function setCookie(d, e, b) { var c = ""; if (b) { var a = new Date; a.setTime(a.getTime() + 864e5 * b), c = "; expires=" + a.toUTCString() } document.cookie = d + "=" + (e || "") + c + "; path=/" } function getCookie(e) { for (var c = e + "=", d = document.cookie.split(";"), b = 0; b < d.length; b++) { for (var a = d[b]; " " == a.charAt(0);)a = a.substring(1, a.length); if (0 == a.indexOf(c)) return a.substring(c.length, a.length) } return null } function eraseCookie(a) { document.cookie = a + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;" } function onclickdisclaimer() { document.getElementById("bottom-disclaimer").innerHTML = "", setCookie("accept-cookies", "1", 10950), location.reload() } function onclickremovedisclaimer() { setCookie("accept-cookies", "0", 10950), document.cookie = "accept-cookies=; expires=Thu, 01-Jan-70 00:00:01 GMT;", document.getElementById("bottom-disclaimer").innerHTML = '<div id="cookieinfo"><div onclick="onclickdisclaimer()" id="cookieinfo-close">OK</div><div id="cookieinfo-text">Ao usar esse site, você aceita nossos termos de uso e política de privacidade, saiba mais <a href="'+privacy_policy+'" title="Pol\xedtica de privacidade" target="_blank" rel="noopener nofollow" style="color:white;font-weight:800">clicando aqui</a>.</div></div>', location.reload() } function refreshTime() { var a = new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" }).replace(", ", " - "); document.getElementById("curr-time-clock").innerHTML = a }
if(getCookie("accept-cookies") != 1){
    document.getElementById("bottom-disclaimer").innerHTML = '<div id="cookieinfo"><div onclick="onclickdisclaimer()" id="cookieinfo-close">OK</div><div id="cookieinfo-text">Ao usar esse site, você aceita nossos termos de uso e política de privacidade, saiba mais <a href="'+privacy_policy+'" title="Pol\xedtica de privacidade" target="_blank" rel="noopener nofollow" style="color:white;font-weight:800">clicando aqui</a>.</div></div>';
}