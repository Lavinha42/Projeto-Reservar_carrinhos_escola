function adicionarAoMural() {
    const professor = document.getElementById('nome-professor').innerText;
    const carrinho = document.getElementById('carrinho').value;
    const sala = document.getElementById('sala').value;
    const horario = document.getElementById('id_periodo').value;

    if (!carrinho || !sala || !horario) {
        alert("Por favor, preencha todos os campos!");
        return;
    }

    const mural = document.getElementById('grid-mural');
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <strong>${professor}</strong><br>
        <small>ID Equipamento: ${carrinho}</small><br>
        <strong>Local:</strong> ${sala}<br>
        <strong>Horário:</strong> ${horario}
    `;
    mural.appendChild(card);

    document.getElementById('sala').value = '';
    document.getElementById('id_periodo').value = '';
}

document.addEventListener('DOMContentLoaded', function () {
    const campoData = document.getElementById('id_data');
    const campoPeriodo = document.getElementById('id_periodo');
    const selectCarrinho = document.getElementById('carrinho');
    const gridMural = document.getElementById('grid-mural');
    const infoQuantidade = document.getElementById('quantidade-info');

    function desabilitarHorariosPassados() {
            const dataInput = campoData.value;
            const hoje = new Date().toISOString().split('T')[0];
            const agora = new Date();
            const horaAtual = agora.getHours();
            const minAtual = agora.getMinutes();

            const options = campoPeriodo.querySelectorAll('option');
            options.forEach(opt => {
                // Verifica se a opção tem um valor de horário (ignora o "Selecione o Horário")
                if (opt.value && opt.value.includes('|')) {
                    const [hInicio] = opt.value.split('|');
                    const [h, m] = hInicio.split(':').map(Number);
                    
                    // Se for hoje E o horário já passou, desabilita
                    if (dataInput === hoje && (h < horaAtual || (h === horaAtual && m < minAtual))) {
                        opt.disabled = true;
                    } else {
                        opt.disabled = false;
                    }
                }
            });
        }

    function atualizarMural() {
        const dataSelecionada = campoData.value;
        if (dataSelecionada) {
            fetch(`/ajax/mural-filtrado/?data=${dataSelecionada}`)
                .then(response => response.text())
                .then(html => {
                    gridMural.innerHTML = html;
                })
                .catch(error => console.error('Erro ao carregar o mural:', error));
        }
    }

    function definirHorarios() {
        let valor = document.getElementById("id_periodo").value;
        if (valor) {
            let partes = valor.split("|");
            document.getElementById("horario_inicio").value = partes[0];
            document.getElementById("horario_fim").value = partes[1];
        }
    }

    function atualizarCarrinhos() {
        const data = campoData.value;
        const periodo = campoPeriodo.value;

        infoQuantidade.innerHTML = '-';

        if (data && periodo) {
            let partes = periodo.split("|");
            let horario_inicio = partes[0];
            let horario_fim = partes[1];

            fetch(`/ajax/disponiveis/?data=${data}&horario_inicio=${horario_inicio}&horario_fim=${horario_fim}`)
                .then(response => response.json())
                .then(dados => {
                    selectCarrinho.innerHTML = '<option value="">Qual carrinho?</option>';
                    dados.equipamentos.forEach(item => {
                        const option = new Option(`${item.nome}`, item.id);
                        option.dataset.quantidade = item.quantidade;
                        selectCarrinho.add(option);
                    });
                    selectCarrinho.disabled = false;
                })
                .catch(error => console.error('Erro ao buscar equipamentos:', error));
        } else {
            selectCarrinho.disabled = true;
            selectCarrinho.innerHTML = '<option value="">Selecione data e período...</option>';
        }
    }
    

    selectCarrinho.addEventListener('change', function () {
        const valorSelecionado = selectCarrinho.value;

        if (valorSelecionado === "") {
            infoQuantidade.innerHTML = `Quantidade Atual: -`;
            return;
        }

        const opcaoSelecionada = selectCarrinho.options[selectCarrinho.selectedIndex];
        const quantidade = opcaoSelecionada.dataset.quantidade;

        if (quantidade !== undefined && quantidade !== null) {
            infoQuantidade.innerHTML = `Quantidade Atual: <strong>${quantidade}</strong>`;
        } else {
            infoQuantidade.innerHTML = `Quantidade Atual: -`;
        }
    });

    campoPeriodo.addEventListener('change', () => {
        definirHorarios();
        atualizarCarrinhos();
    });
    desabilitarHorariosPassados();
    campoData.addEventListener('change', () => {
        atualizarMural();
        atualizarCarrinhos();
        desabilitarHorariosPassados();
    });
    window.definirHorarios = definirHorarios;
    atualizarMural();
});