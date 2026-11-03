const SUPABASE_URL = 'https://bccnthfwbnvkbfwdelns.supabase.co/rest/v1/';
const SUPABASE_KEY = 'sb_publishable_4rdZ_ed3QCPihQlyovgmnA_SbioXzYn';

const client = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

let dadosGlobais = [];
let abaAtiva = 'Casal'; // Prioridade inicial para contas conjuntas

document.addEventListener('DOMContentLoaded', () => {
    carregarDados();
    
    // Configura data atual
    document.getElementById('data_vencimento').valueAsDate = new Date();

    // Dinâmica do formulário: Mostra "Quem pagou" apenas se for Casal e estiver Pago
    const responsavelEl = document.getElementById('responsavel');
    const statusEl = document.getElementById('status');
    
    const atualizarCamposForm = () => {
        const divQuemPagou = document.getElementById('div_quem_pagou');
        const quemPagouSelect = document.getElementById('quem_pagou');
        
        if (responsavelEl.value === 'Casal' && statusEl.value === 'Pago') {
            divQuemPagou.classList.remove('hidden');
            quemPagouSelect.required = true;
        } else {
            divQuemPagou.classList.add('hidden');
            quemPagouSelect.required = false;
            quemPagouSelect.value = '';
        }
    };

    responsavelEl.addEventListener('change', atualizarCamposForm);
    statusEl.addEventListener('change', atualizarCamposForm);

    // Envio do formulário
    document.getElementById('form-lancamento').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const registro = {
            descricao: document.getElementById('descricao').value,
            valor: parseFloat(document.getElementById('valor').value),
            data_vencimento: document.getElementById('data_vencimento').value,
            categoria: document.getElementById('categoria').value || 'Geral',
            forma_pagamento: document.getElementById('forma_pagamento').value,
            status: document.getElementById('status').value,
            responsavel: document.getElementById('responsavel').value,
            quem_pagou: document.getElementById('quem_pagou').value || null
        };

        const { error } = await client.from('financas_casal').insert([registro]);
        
        if (error) {
            alert('Erro ao salvar: ' + error.message);
        } else {
            document.getElementById('descricao').value = '';
            document.getElementById('valor').value = '';
            document.getElementById('categoria').value = '';
            atualizarCamposForm();
            carregarDados();
        }
    });
});

async function carregarDados() {
    const { data, error } = await client
        .from('financas_casal')
        .select('*')
        .order('data_vencimento', { ascending: true });

    if (error) {
        console.error('Erro ao buscar dados:', error);
        return;
    }

    dadosGlobais = data;
    renderizarInterface();
}

function mudarAba(aba) {
    abaAtiva = aba;
    
    // Atualiza CSS das abas
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if(btn.id === `aba-${aba}`) {
            btn.classList.add('text-indigo-600', 'border-indigo-600');
            btn.classList.remove('text-slate-500', 'border-transparent');
        } else {
            btn.classList.remove('text-indigo-600', 'border-indigo-600');
            btn.classList.add('text-slate-500', 'border-transparent');
        }
    });

    // Atualiza o select do form para bater com a aba atual automaticamente
    document.getElementById('responsavel').value = aba;
    document.getElementById('responsavel').dispatchEvent(new Event('change'));

    renderizarInterface();
}

function renderizarInterface() {
    document.getElementById('titulo-tabela').textContent = `Lançamentos: ${abaAtiva}`;
    
    const dadosFiltrados = dadosGlobais.filter(d => d.responsavel === abaAtiva);
    renderizarTabela(dadosFiltrados);
    
    // O balanço sempre calcula baseado nos dados globais (apenas Casal que já foi Pago)
    calcularBalanco(dadosGlobais);
}

function renderizarTabela(dados) {
    const tbody = document.getElementById('tabela-corpo');
    tbody.innerHTML = '';

    dados.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition';
        
        // Ajuste de data considerando fuso
        const dataFormatada = new Date(item.data_vencimento + 'T00:00:00').toLocaleDateString('pt-BR');
        const valorFormatado = item.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        
        // Cores dos status
        let corStatus = 'bg-slate-100 text-slate-700';
        if (item.status === 'Pago') corStatus = 'bg-emerald-100 text-emerald-700';
        if (item.status === 'Pendente') corStatus = 'bg-amber-100 text-amber-700';
        if (item.status === 'Atrasado') corStatus = 'bg-red-100 text-red-700';

        let extraQuemPagou = '';
        if (item.responsavel === 'Casal' && item.status === 'Pago' && item.quem_pagou) {
            extraQuemPagou = `<br><span class="text-xs text-emerald-600">por ${item.quem_pagou}</span>`;
        }

        tr.innerHTML = `
            <td class="p-4 text-sm text-slate-600">${dataFormatada}</td>
            <td class="p-4 text-sm text-slate-800 font-medium">${item.descricao}</td>
            <td class="p-4 text-sm text-slate-500">${item.categoria}</td>
            <td class="p-4 text-sm text-slate-500">${item.forma_pagamento}</td>
            <td class="p-4 text-sm">
                <span class="px-2 py-1 rounded text-xs font-semibold ${corStatus}">${item.status}</span>
                ${extraQuemPagou}
            </td>
            <td class="p-4 text-sm text-slate-800 font-semibold text-right">${valorFormatado}</td>
        `;
        tbody.appendChild(tr);
    });
}

function calcularBalanco(dados) {
    let totalHenrique = 0;
    let totalCamila = 0;

    // A regra de acerto se aplica APENAS a contas do Casal que já foram Pagas
    dados.filter(d => d.responsavel === 'Casal' && d.status === 'Pago').forEach(item => {
        if (item.quem_pagou === 'Henrique') totalHenrique += Number(item.valor);
        if (item.quem_pagou === 'Camila') totalCamila += Number(item.valor);
    });

    document.getElementById('total-henrique').textContent = totalHenrique.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    document.getElementById('total-camila').textContent = totalCamila.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    const statusAcerto = document.getElementById('status-acerto');
    const diferenca = totalHenrique - totalCamila;
    const valorAcerto = Math.abs(diferenca / 2).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    if (diferenca > 0) {
        statusAcerto.innerHTML = `Camila deve<br><span class="text-3xl">${valorAcerto}</span>`;
    } else if (diferenca < 0) {
        statusAcerto.innerHTML = `Henrique deve<br><span class="text-3xl">${valorAcerto}</span>`;
    } else {
        statusAcerto.innerHTML = `Tudo quite!<br><span class="text-3xl">R$ 0,00</span>`;
    }
}