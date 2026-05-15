function adicionarAoMural() {
    const professor = document.getElementById('nome-professor').innerText;
    const carrinho = document.getElementById('carrinho').value;
    const sala = document.getElementById('sala').value;
    const horario = document.getElementById('horario').value;

    if(!carrinho || !sala || !horario) {
        alert("Por favor, preencha todos os campos!");
        return;
    }

    const mural = document.getElementById('grid-mural');
    
    // Criação do card
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <strong>${professor}</strong><br>
        <small>${carrinho}</small><br>
        <strong>Local:</strong> ${sala}<br>
        <strong>Horário:</strong> ${horario}
    `;

    mural.appendChild(card);

    // Limpar campos
    document.getElementById('sala').value = '';
    document.getElementById('horario').value = '';
}
document.addEventListener('DOMContentLoaded', function() {
    const campoData = document.getElementById('id_data');
    const campoPeriodo = document.getElementById('id_periodo');
    const selectCarrinho = document.getElementById('carrinho');
    const gridMural = document.getElementById('grid-mural');

    // Atualiza o Mural (Cards)
    function atualizarMural() {
        const data = campoData.value;
        if (data) {
            fetch(`/ajax/mural-filtrado/?data=${data}`)
                .then(response => response.text())
                .then(html => {
                    gridMural.innerHTML = html;
                });
        }
    }

    // Atualiza o Select de Carrinhos
    function atualizarCarrinhos() {
        const data = campoData.value;
        const periodo = campoPeriodo.value;

        if (data && periodo) {
            fetch(`/ajax/disponiveis/?data=${data}&periodo=${periodo}`)
                .then(response => response.json())
                .then(dados => {
                    selectCarrinho.innerHTML = '<option value="">Qual carrinho?</option>';
                    dados.equipamentos.forEach(item => {
                        selectCarrinho.add(new Option(item.nome, item.id));
                    });
                    selectCarrinho.disabled = false;
                });
        } else {
            selectCarrinho.disabled = true;
            selectCarrinho.innerHTML = '<option value="">Selecione data e período...</option>';
        }
    }

    // Escuta mudanças nos campos
    campoData.addEventListener('change', () => {
        atualizarMural();
        atualizarCarrinhos();
    });

    campoPeriodo.addEventListener('change', atualizarCarrinhos);
});
document.addEventListener('DOMContentLoaded', function() {
    const campoData = document.getElementById('id_data');
    const gridMural = document.getElementById('grid-mural');

    // Função que busca as reservas no servidor
    function atualizarMural() {
        const dataSelecionada = campoData.value;

        if (dataSelecionada) {
            // Faz a chamada para a URL do Django
            fetch(`/ajax/mural-filtrado/?data=${dataSelecionada}`)
                .then(response => response.text()) // Recebe o HTML puro
                .then(html => {
                    gridMural.innerHTML = html; // Substitui o mural atual pelo novo
                })
                .catch(error => console.error('Erro ao carregar o mural:', error));
        }
    }

    // Escuta toda vez que a data for alterada
    campoData.addEventListener('change', atualizarMural);
});