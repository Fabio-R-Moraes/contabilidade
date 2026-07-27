/*=========================================================
   Finança Familiar - Extrato de conta
   Checkboxes de conferência + scroll automático para o final
===========================================================*/

document.addEventListener('DOMContentLoaded', function() {
    //Configuração via data-attributes
    const _meta = document.getElementById('extrato-meta');
    const contaPk = _meta ? _meta.getAttribute('data-conta-pk') : '';
    const tipoConta = _meta ? _meta.getAttribute('data-tipo-conta') : '';
    const STORAGE_KEY = 'extrato_checks_' + contaPk + '_' + tipoConta;

    //Carregar estado salvo em localStorage
    function getChecks() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
        catch { return {}; }
    }

    function saveChecks(checks) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(checks));
    }

    //Aplicar estado salvo ao carregar a página
    const checks = getChecks();
    document.querySelectorAll('.check-lancamento').forEach(function (cb) {
        const id = cb.dataset.id;

        if (checks[id]) {
            cb.checked = true;
            cb.closest('tr').classList.add('conferido');
        }

        cb.addEventListener('change', function () {
            const row = this.closest('tr');
            const current = getChecks();

            if (this.checked) {
                current[id] = true;
                row.classList.add('conferido');
            } else {
                delete current[id];
                row.classList.remove('conferido');
            }
            saveChecks(current);
        });
    });

    //Ir ao final da página ao carregar
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

    //Botão desmarcar todos
    document.getElementById('btn-limpar-checks').addEventListener('click', function () {
        localStorage.removeItem(STORAGE_KEY);
        document.querySelectorAll('.check-lancamento').forEach(function (cb) {
            cb.checked = false;
            cb.closest('tr').classList.remove('conferido');
        });
    });
});