/*==================================================================
  Financa Familiar - Lancamento: Formset de partidas
  ==================================================================*/
document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('partidas-container');
    const totalFormsInput = document.querySelector('[name="partidas-TOTAL_FORMS"]');
    const template = document.getElementById('partida-template');

    //So executa na página do formulario de lancamentos
    if (!container || !totalFormsInput || !template) return;

    //Inicializar comportamento das linhas ja renderizadas
    initPartidaRow(container);

    // _________ Adicionar nova partida _______________
    document.getElementById('add-partida').addEventListener('click', function () {
        const idx = parseInt(totalFormsInput.value);
        const html = template.innerHTML.replaceAll('__prefix__', idx);
        const div = document.createElement('div');
        div.innerHTML = html
        const row = div.firstElementChild;
        container.appendChild(row);
        totalFormsInput.value = idx + 1;

        initPartidaRow(row);
        updateBalance();
    });

    // __________ Remover partida (Event delegation) ___________
    container.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-remove-row');

        if (!btn) return;

        const row = btn.closest('.partida-row');
        const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');

        if (deleteCheckbox) {
            //Linha ja persistida, marcar para deletar
            deleteCheckbox.checked = true;
            row.style.opacity = '0.3';
            row.style.pointerEvents = 'none';
        } else {
            //Linha nova: remover do DOM
            row.remove();
        }

        updateBalance();
    });

    // ____________ Recalcular ao alterar valor ou tipo ______________
    container.addEventListener('input', updateBalance);

    container.addEventListener('change', function(e) {
        //Atualizar a cor da borda conforme o D/C selecionado
        const tipoSelect = e.target.closest('[name$="-tipo"]');

        if (tipoSelect) {
            const row = tipoSelect.closest('.partida-row');
            row.classList.remove('tipo-debito', 'tipo-credito');

            if (tipoSelect.value === 'DEBITO') row.classList.add('tipo-debito');
            if (tipoSelect.value === 'CREDITO') row.classList.add('tipo-credito');
        }
        updateBalance();
    });

    // ___________ Inicializar uma linha (ou o container inteiro) ________________
    function initPartidaRow(scope) {
        //Mostrar/ocultar campos de conta conforme tipo selecionado
        scope.querySelectorAll('.tipo-conta-select').forEach(function (sel) {
            toggleContaFields(sel);
            sel.addEventListener('change', function () { toggleContaFields(this); });
        });

        //Aplicar classe de cor nas linhas existentes
        scope.querySelectorAll('[name$="-tipo"]').forEach(function (sel) {
            const row = sel.closest('.partida-row');

            if (!row) return;

            row.classList.remove('tipo-debito', 'tipo-credito');

            if (sel.value === 'DEBITO') row.classList.add('tipo-debito');
            if (sel.value === 'CREDITO') row.classList.add('tipo-credito');
        });
    }

    //__________ Alternar exibicao de conta credora/devedora ______________
    function toggleContaFields(sel) {
        const row = sel.closest('.partida-row');
        const credoraW = row.querySelector('.conta-credora-wrapper');
        const devedoraW = row.querySelector('.conta-devedora-wrapper');

        if (sel.value === 'devedora') {
            credoraW.style.display = 'none';
            devedoraW.style.display = '';
        } else {
            credoraW.style.display = '';
            devedoraW.style.display = 'none';
        }
    }

    //_________ Calcular e exibir totais de debito/credito ______________
    function updateBalance() {
        let debitos = 0;
        let creditos = 0;

        container.querySelectorAll('.partida-row').forEach(function (row) {
            //Ignorar linhas marcadas para deletar
            if (row.style.opacity === '0.3') return;

            const deleteCheck = row.querySelector('input[type="checbox"][name$="-DELETE"]');

            if (deleteCheck && deleteCheck.checked) return;

            const tipoSel = row.querySelector('[name$="-tipo"]');
            const valorInput = row.querySelector('.valor-partida');

            if (!tipoSel || !valorInput) return;

            const val = parseFloat(valorInput.value) || 0;

            if (tipoSel.value === 'DEBITO') debitos += val;
            else creditos += val;
        });

        //Atualizar elementos de exibicao
        document.getElementById('total-debitos').textContent = 'R$ ' + debitos.toFixed(2).replace('.', ',');
        document.getElementById('total-creditos').textContent = 'R$ ' + creditos.toFixed(2).replace('.', ',');

        const diff = Math.abs(debitos - creditos);

        document.getElementById('diferenca').textContent = 'R$ ' + diff.toFixed(2).replace('.', ',');

        const statusCard = document.getElemmentById('balance-status');
        const icon = document.getElementById('balance-icon');
        const difEl = document.getElementById('diferenca');

        if (debitos > 0 && creditos > 0 && diff < 0.005) {
            //Balanceado
            statusCard.className = 'card border-success';
            icon.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> Balanceado!</span>';
            difEl.classList.remove('text-danger');
            difEl.classList.add('text-success');
        } else {
            //Desbalanceado
            statusCard.className = 'card border-warning';
            icon.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-triangle-fill"></i> Desbalanceado...</span>';
            difEl.classList.remove('text-success');
            difEl.classList.add('text-danger');
        }
    }

    //Calcular ao carregar a página
    updateBalance();
});
