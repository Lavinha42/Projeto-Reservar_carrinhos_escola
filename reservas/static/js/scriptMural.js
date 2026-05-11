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

    //Procurar reservas já existentes
    const cardExistente = document.querySelectorAll('.card');

    for(let card of cardExistente) {

        const texttoCard = card.innerText;

        // Verificar se já existe mesma reserva
        if(
            texttoCard.includes(carrinho) &&
            texttoCard.includes(sala) &&
            texttoCard.includes(horario)
        ) {
            alert("Essa reserva já existe!");
        }
    }
    
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