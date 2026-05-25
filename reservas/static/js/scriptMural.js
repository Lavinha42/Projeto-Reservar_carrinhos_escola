// 1. Função global para adicionar manualmente ao mural (se aplicável)
function adicionarAoMural() {
    const professor = document.getElementById('nome-professor').innerText;
    const carrinho = document.getElementById('carrinho').value;
    const sala = document.getElementById('sala').value;
    const horario = document.getElementById('id_periodo').value; // Corrigido para o ID correto do seu HTML

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
        <small>ID Equipamento: ${carrinho}</small><br>
        <strong>Local:</strong> ${sala}<br>
        <strong>Horário:</strong> ${horario}
    `;

    mural.appendChild(card);

    // Limpar campos
    document.getElementById('sala').value = '';
    document.getElementById('id_periodo').value = '';
}

// 2. Centralização de todos os eventos após o carregamento da página
document.addEventListener('DOMContentLoaded', function() {
    // Declaração de todas as variáveis do DOM
    const campoData = document.getElementById('id_data');
    const campoPeriodo = document.getElementById('id_periodo');
    const selectCarrinho = document.getElementById('carrinho');
    const gridMural = document.getElementById('grid-mural');
    const infoQuantidade = document.getElementById('quantidade-info');

    // Função que Atualiza o Mural (Cards) buscando do servidor Django
    function atualizarMural() {
        const dataSelecionada = campoData.value;
        if (dataSelecionada) {
            fetch(`/ajax/mural-filtrado/?data=${dataSelecionada}`)
                .then(response => response.text()) // Recebe o HTML puro
                .then(html => {
                    gridMural.innerHTML = html; // Substitui o mural atual pelo novo
                })
                .catch(error => console.error('Erro ao carregar o mural:', error));
        }
    }

    // Função que Atualiza o Select de Carrinhos e reseta o texto de quantidade
// Função que Atualiza o Select de Carrinhos e reseta o texto de quantidade
    function atualizarCarrinhos() {
        const data = campoData.value;
        const periodo = campoPeriodo.value;
        console.log('data:', data, '| periodo:', periodo); // ← adiciona isso

        // Sempre que mudar a data/período, reseta a exibição da quantidade para o traço
        infoQuantidade.innerHTML = '-';

        if (data && periodo) {
            fetch(`/ajax/disponiveis/?data=${data}&periodo=${periodo}`)
                .then(response => response.json())
                .then(dados => {
                    selectCarrinho.innerHTML = '<option value="">Qual carrinho?</option>';
                    
                    dados.equipamentos.forEach(item => {
                        const option = new Option(
                            `${item.nome}`,
                            item.id
                        );
                        // Garante que a quantidade vinda do Django seja salva no HTML da opção
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


    // EVENTO CHAVE: Monitora quando o usuário clica/seleciona um equipamento desejado
    selectCarrinho.addEventListener('change', function() {
        const valorSelecionado = selectCarrinho.value;
        
        if (valorSelecionado === "") {
            infoQuantidade.innerHTML = `Quantidade Atual: -`;
            return;
        }

        // Pega a opção que está ativamente selecionada pelo usuário
        const opcaoSelecionada = selectCarrinho.options[selectCarrinho.selectedIndex];
        // Obtém a quantidade guardada no dataset
        const quantidade = opcaoSelecionada.dataset.quantidade;

        if (quantidade !== undefined && quantidade !== null) {
            infoQuantidade.innerHTML = `Quantidade Atual: <strong>${quantidade}</strong>`;
        } else {
            infoQuantidade.innerHTML = `Quantidade Atual: -`;
        }
    });

    // Ouvintes de eventos para os filtros de Data e Período

    campoPeriodo.addEventListener('change', () => {
    atualizarCarrinhos();
});
});