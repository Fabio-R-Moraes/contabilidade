(function () {
    //URL do endpoint de auto logout
    var AUTO_LOGOUT_URL = document.body.dataset.autoLogoutUrl;

    if (!AUTO_LOGOUT_URL) return;

    //Flag: true quando o usuário clicou em um link ou submeteu um form
    //interno - nesse caso o beforeunload NÃO deve fazer o logout
    var navegacaoInterna = false;

    //Marcar como navegação interna ao clicar em qualquer link do site
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a[href]');

        if (!link) return;

        var href = link.getAttribute('href');

        //Ignorar links externos, âncoras, javascript: e target=_blank
        if (!href || href.startsWith('http') || href.startsWith('#') || href.startsWith('javascript') || link.target === '_blank') return;
        navegacaoInterna = true;
    });

    //Marcar como navegação interna ao submeter qualquer form
    document.addEventListener('submit', function () {
        navegacaoInterna = true;
    });

    function getCookie(name) {
        var value = ';' + document.cookie;
        var parts = value.split(';' + name + '=');

        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    window.addEventListener('beforeunload', function () {
        if (navegacaoInterna) return; //navegação interna, não faz logout

        var csrf = getCookie('csrftoken');

        if (!csrf) return;

        var formData = new FormData();
        formData.append('csrfmiddlewaretoken', csrf);
        navigator.sendBeacon(AUTO_LOGOUT_URL, formData);
    });
})();