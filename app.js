/* ==========================================================================
   DIVIAPP — LÓGICA, SUPABASE REALTIME & DADOS DA PLANILHA (app.js)
   ========================================================================== */

// 1. CONFIGURAÇÃO SUPABASE
const SUPABASE_URL = 'https://mljyikyhadcxkpzojnzv.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Hv9Hirm9bJB1fmvjzLKoRw_AdZPoqi4';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 2. LISTAS OFICIAIS DA ABA 'CATEGORIAS' DA PLANILHA
const categorias = [
    'Moradia', 'Mercado', 'Energia', 'Água', 'Casamento',
    'Telefone', 'Transporte', 'Saúde', 'Lazer', 'Compras pessoais',
    'Cartão de crédito', 'Financiamento', 'Carro', 'Investimentos', 'Outros'
];

const statusList = ['Pendente', 'Pago', 'Atrasado', 'Cancelado'];

const formasPagamento = [
    'Pix', 'Débito', 'Crédito', 'Boleto',
    'Dinheiro', 'Transferência', 'Débito automático'
];

// 3. DADOS REAIS EXTRAÍDOS DA PLANILHA (controle_financeiro - HENRIQUE E CAMILA.xlsx)
const GANHOS_PLANILHA = [
    { mes: '2026-09', responsavel: 'Henrique', valor: 3985.00 },
    { mes: '2026-09', responsavel: 'Camila',   valor: 2860.00 },
    { mes: '2026-10', responsavel: 'Henrique', valor: 3985.00 },
    { mes: '2026-10', responsavel: 'Camila',   valor: 2860.00 },
    { mes: '2026-11', responsavel: 'Henrique', valor: 3985.00 },
    { mes: '2026-11', responsavel: 'Camila',   valor: 2860.00 }
];

const CONTAS_PLANILHA = [
    // --- HENRIQUE: SETEMBRO 2026 (Total: R$ 5.243,00) ---
    { descricao: 'Agua', categoria: 'Água', valor: 120.00, vencimento: '2026-09-21', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Aluguel 08', categoria: 'Moradia', valor: 1103.00, vencimento: '2026-09-01', status: 'Atrasado', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cartão Nubank', categoria: 'Cartão de crédito', valor: 1600.00, vencimento: '2026-09-10', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cartão Sicred', categoria: 'Cartão de crédito', valor: 430.00, vencimento: '2026-09-05', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cemig', categoria: 'Energia', valor: 190.00, vencimento: '2026-09-17', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Internet', categoria: 'Moradia', valor: 100.00, vencimento: '2026-09-10', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Compra', categoria: 'Mercado', valor: 600.00, vencimento: '2026-09-30', status: 'Pago', forma_pagamento: 'Débito automático', responsavel: 'Henrique' },
    { descricao: 'Ajuste de Valor (Aluguel mês 07)', categoria: 'Moradia', valor: 1100.00, vencimento: '2026-09-01', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },

    // --- HENRIQUE: OUTUBRO 2026 (Total: R$ 4.840,00) ---
    { descricao: 'Agua', categoria: 'Água', valor: 120.00, vencimento: '2026-10-21', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Aluguel', categoria: 'Moradia', valor: 500.00, vencimento: '2026-10-01', status: 'Pago', forma_pagamento: 'Débito', responsavel: 'Henrique' },
    { descricao: 'Cartão Nubank', categoria: 'Cartão de crédito', valor: 2000.00, vencimento: '2026-10-10', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cartão Sicred', categoria: 'Cartão de crédito', valor: 430.00, vencimento: '2026-10-05', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cemig', categoria: 'Energia', valor: 170.00, vencimento: '2026-10-17', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Internet', categoria: 'Moradia', valor: 100.00, vencimento: '2026-10-10', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Compra', categoria: 'Mercado', valor: 600.00, vencimento: '2026-10-01', status: 'Pago', forma_pagamento: 'Débito automático', responsavel: 'Henrique' },
    { descricao: 'Ajuste de Valor (Aluguel atrasado)', categoria: 'Moradia', valor: 620.00, vencimento: '2026-10-01', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Transporte', categoria: 'Transporte', valor: 150.00, vencimento: '2026-10-30', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Material de Limpeza', categoria: 'Mercado', valor: 150.00, vencimento: '2026-10-15', status: 'Pago', forma_pagamento: 'Crédito', responsavel: 'Henrique' },

    // --- HENRIQUE: NOVEMBRO 2026 (Total: R$ 3.028,06) ---
    { descricao: 'Agua', categoria: 'Água', valor: 120.00, vencimento: '2026-11-20', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Aluguel', categoria: 'Moradia', valor: 500.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cartão Nubank', categoria: 'Cartão de crédito', valor: 967.00, vencimento: '2026-11-17', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cartão Sicred', categoria: 'Cartão de crédito', valor: 306.00, vencimento: '2026-11-08', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cemig', categoria: 'Energia', valor: 125.85, vencimento: '2026-11-17', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Internet', categoria: 'Moradia', valor: 100.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Compra', categoria: 'Mercado', valor: 600.00, vencimento: '2026-11-30', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Cemig (mes 10)', categoria: 'Moradia', valor: 159.21, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Henrique' },
    { descricao: 'Transporte', categoria: 'Transporte', valor: 150.00, vencimento: '2026-11-10', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Henrique' },

    // --- CAMILA: OUTUBRO 2026 (Total: R$ 1.837,00) ---
    { descricao: 'Cartão credito', categoria: 'Cartão de crédito', valor: 500.00, vencimento: '2026-10-08', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Vivo', categoria: 'Telefone', valor: 70.00, vencimento: '2026-10-12', status: 'Pendente', forma_pagamento: 'Crédito', responsavel: 'Camila' },
    { descricao: 'remédio', categoria: 'Saúde', valor: 80.00, vencimento: '2026-10-07', status: 'Pago', forma_pagamento: 'Crédito', responsavel: 'Camila' },
    { descricao: 'Transporte (Pago 1 semana)', categoria: 'Transporte', valor: 210.00, vencimento: '2026-10-07', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Consultas', categoria: 'Saúde', valor: 117.00, vencimento: '2026-10-09', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Netflix', categoria: 'Lazer', valor: 60.00, vencimento: '2026-10-01', status: 'Pago', forma_pagamento: 'Crédito', responsavel: 'Camila' },
    { descricao: 'Aluguel', categoria: 'Moradia', valor: 500.00, vencimento: '2026-10-01', status: 'Pago', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Carne', categoria: 'Mercado', valor: 300.00, vencimento: '2026-10-18', status: 'Pago', forma_pagamento: 'Crédito', responsavel: 'Camila' },

    // --- CAMILA: NOVEMBRO 2026 (Total: R$ 2.865,36) ---
    { descricao: 'Remédio', categoria: 'Saúde', valor: 160.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Aluguel', categoria: 'Moradia', valor: 500.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Cartão Bradesco', categoria: 'Cartão de crédito', valor: 680.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Cartão Nubank', categoria: 'Cartão de crédito', valor: 967.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Transporte', categoria: 'Transporte', valor: 264.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Crédito', responsavel: 'Camila' },
    { descricao: 'vivo', categoria: 'Telefone', valor: 131.36, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Crédito', responsavel: 'Camila' },
    { descricao: 'shoppe', categoria: 'Compras pessoais', valor: 45.00, vencimento: '2026-11-30', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' },
    { descricao: 'Atum de Minas', categoria: 'Mercado', valor: 118.00, vencimento: '2026-11-10', status: 'Pendente', forma_pagamento: 'Pix', responsavel: 'Camila' }
];

// 4. ESTADO GLOBAL DA APLICAÇÃO
let contas = [];
let ganhos = [];
let investimentos = [];
let dividas = [];
let grafico = null;
let abaAtual = 'dashboard';

// Metadados dos Títulos das Abas
const infoAbas = {
    dashboard: {
        titulo: 'Dashboard do Casal',
        subtitulo: 'Visão consolidada das receitas, despesas e investimentos do mês'
    },
    henrique: {
        titulo: '<img src="assets/avatar-henrique.png" alt="Henrique" class="w-5 h-5 rounded-full object-cover inline-block align-middle mr-1.5">Contas Henrique',
        subtitulo: 'Gestão de renda individual, métricas e lançamentos do Henrique'
    },
    camila: {
        titulo: '<img src="assets/avatar-camila.png" alt="Camila" class="w-5 h-5 rounded-full object-cover inline-block align-middle mr-1.5">Contas Camila',
        subtitulo: 'Gestão de renda individual, métricas e lançamentos da Camila'
    },
    investimentos: {
        titulo: '<img src="assets/icone-investimentos.png" alt="Investimentos" class="w-5 h-5 rounded-full object-cover inline-block align-middle mr-1.5">Hub de Investimentos',
        subtitulo: 'Acompanhamento de aportes, rendimentos mensais e evolução patrimonial'
    },
    controle: {
        titulo: '🎯 Controle Ideal',
        subtitulo: 'Compare os gastos do mês com a distribuição ideal da renda do casal'
    },
    dividas: {
        titulo: '💳 Dívidas',
        subtitulo: 'Mapeamento de passivos do Henrique e da Camila (não afeta as outras abas)'
    }
};

// ==========================================================================
// INICIALIZAÇÃO E TEMPO REAL (SUPABASE REALTIME)
// ==========================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Define o mês de referência inicial como 2026-11 (mês base configurado na planilha)
    const inputMes = document.getElementById('mesGlobal');
    inputMes.value = '2026-11';

    // Data padrão no formulário de investimento
    const invData = document.getElementById('inv-data');
    if (invData) invData.value = '2026-11-10';

    // Gera os formulários dinâmicos de Henrique e Camila
    gerarFormConta('form-henrique', 'Henrique');
    gerarFormConta('form-camila', 'Camila');

    // Carrega os dados iniciais e verifica se precisa popular com a planilha
    await carregarDados(true);
    await carregarDividas();

    // Ativa escuta em Tempo Real no Supabase (Postgres Changes)
    iniciarRealtimeSupabase();
});

function iniciarRealtimeSupabase() {
    try {
        supabaseClient
            .channel('diviapp-realtime-sync')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'contas' }, () => carregarDados(false))
            .on('postgres_changes', { event: '*', schema: 'public', table: 'ganhos' }, () => carregarDados(false))
            .on('postgres_changes', { event: '*', schema: 'public', table: 'investimentos' }, () => carregarDados(false))
            .on('postgres_changes', { event: '*', schema: 'public', table: 'dividas' }, () => carregarDividas())
            .subscribe((status) => {
                const dot = document.getElementById('status-dot');
                const txt = document.getElementById('status-text');
                if (status === 'SUBSCRIBED') {
                    if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse';
                    if (txt) txt.innerText = 'Tempo Real Ativo';
                }
            });
    } catch (err) {
        console.warn('Aviso Realtime:', err);
    }
}

// ==========================================================================
// NAVEGAÇÃO E UTILITÁRIOS VISUAIS
// ==========================================================================

function mudarAba(abaId) {
    abaAtual = abaId;

    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(abaId).classList.add('active');
    document.getElementById('btn-' + abaId).classList.add('active');

    // Atualiza cabeçalho
    if (infoAbas[abaId]) {
        document.getElementById('page-title').innerHTML = infoAbas[abaId].titulo;
        document.getElementById('page-subtitle').innerText = infoAbas[abaId].subtitulo;
    }

    carregarDados(false);
}

function navegarMes(direcao) {
    const input = document.getElementById('mesGlobal');
    if (!input.value) return;
    const [ano, mes] = input.value.split('-').map(Number);
    const data = new Date(ano, mes - 1 + direcao, 1);
    const novoAno = data.getFullYear();
    const novoMes = String(data.getMonth() + 1).padStart(2, '0');
    input.value = `${novoAno}-${novoMes}`;
    carregarDados(false);
}

function toggleForm(formId) {
    const form = document.getElementById(formId);
    form.classList.toggle('hidden');
}

const formatarMoeda = (valor) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(valor) || 0);

const formatarDataBR = (isoDate) => {
    if (!isoDate) return '-';
    return isoDate.split('-').reverse().join('/');
};

function mostrarToast(mensagem, tipo = 'sucesso') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const cores = {
        sucesso: 'bg-slate-900 text-white border-emerald-500',
        aviso: 'bg-slate-900 text-white border-amber-500',
        erro: 'bg-rose-600 text-white border-rose-300'
    };

    toast.className = `pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg border-l-4 text-xs sm:text-sm font-semibold transition-all duration-300 ${cores[tipo] || cores.sucesso}`;
    toast.innerHTML = `<span>${tipo === 'erro' ? '⚠️' : '✅'}</span><span>${mensagem}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(12px)';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

// ==========================================================================
// LEITURA E SINCRONIZAÇÃO COM O BANCO DE DADOS (SUPABASE)
// ==========================================================================

async function carregarDados(verificarSeedInicial = false) {
    const mesSelecionado = document.getElementById('mesGlobal').value;

    try {
        const [resContas, resGanhos, resInvest] = await Promise.all([
            supabaseClient.from('contas').select('*').order('vencimento', { ascending: true }),
            supabaseClient.from('ganhos').select('*').eq('mes', mesSelecionado),
            supabaseClient.from('investimentos').select('*').order('data', { ascending: false })
        ]);

        if (resContas.error) throw resContas.error;

        contas = resContas.data || [];
        ganhos = resGanhos.data || [];
        investimentos = resInvest.data || [];

        // Se o banco estiver completamente vazio no primeiro acesso, popula com os dados da planilha
        if (verificarSeedInicial && contas.length === 0) {
            await sincronizarPlanilhaPadrao(false);
            return;
        }

        // Filtra pelo mês global selecionado
        const contasMes = contas.filter(c => c.vencimento && c.vencimento.startsWith(mesSelecionado));
        const investMes = investimentos.filter(i => i.data && i.data.startsWith(mesSelecionado));

        atualizarTelas(contasMes, investMes, ganhos);
    } catch (err) {
        console.error('Erro ao carregar do Supabase, usando dados locais da planilha:', err);
        const contasMes = CONTAS_PLANILHA.filter(c => c.vencimento.startsWith(mesSelecionado));
        const ganhosMes = GANHOS_PLANILHA.filter(g => g.mes === mesSelecionado);
        atualizarTelas(contasMes, [], ganhosMes);
    }
}

// Importa/Atualiza os dados da planilha Excel no Supabase sem duplicar registros
async function sincronizarPlanilhaPadrao(exibirConfirmacao = true) {
    if (exibirConfirmacao) {
        const ok = confirm('Deseja sincronizar o banco de dados com todos os lançamentos e ganhos da planilha (Setembro, Outubro e Novembro/2026)?');
        if (!ok) return;
    }

    mostrarToast('Sincronizando dados da planilha com o Supabase...', 'aviso');

    try {
        // 1. Sincroniza Ganhos Mensais (Henrique R$ 3.985,00 | Camila R$ 2.860,00)
        const { data: ganhosAtuais } = await supabaseClient.from('ganhos').select('*');
        const listaGanhosBanco = ganhosAtuais || [];

        for (const item of GANHOS_PLANILHA) {
            const existente = listaGanhosBanco.find(
                g => g.mes === item.mes && g.responsavel === item.responsavel
            );
            if (existente) {
                await supabaseClient.from('ganhos').update({ valor: item.valor }).eq('id', existente.id);
            } else {
                await supabaseClient.from('ganhos').insert([item]);
            }
        }

        // 2. Sincroniza as 43 Contas da Planilha evitando duplicatas
        const { data: contasAtuais } = await supabaseClient.from('contas').select('*');
        const listaContasBanco = contasAtuais || [];
        const novasContasParaInserir = [];

        for (const contaPlanilha of CONTAS_PLANILHA) {
            const jaExiste = listaContasBanco.some(
                c =>
                    c.responsavel === contaPlanilha.responsavel &&
                    c.vencimento === contaPlanilha.vencimento &&
                    Math.abs(Number(c.valor) - Number(contaPlanilha.valor)) < 0.01 &&
                    c.descricao.toLowerCase().trim() === contaPlanilha.descricao.toLowerCase().trim()
            );

            if (!jaExiste) {
                novasContasParaInserir.push(contaPlanilha);
            }
        }

        if (novasContasParaInserir.length > 0) {
            await supabaseClient.from('contas').insert(novasContasParaInserir);
        }

        mostrarToast(`Planilha sincronizada! (${novasContasParaInserir.length} novos registros adicionados)`);
        await carregarDados(false);
    } catch (err) {
        console.error('Erro ao sincronizar planilha:', err);
        mostrarToast('Erro ao sincronizar com o banco. Verifique a conexão.', 'erro');
    }
}

// ==========================================================================
// OPERAÇÕES CRUD (RENDA, CONTAS COM DIVISÃO CASAL E INVESTIMENTOS)
// ==========================================================================

// Salvar Ganho Individual
async function salvarGanho(pessoa) {
    const mes = document.getElementById('mesGlobal').value;
    const inputEl = document.getElementById(`ganho-${pessoa.toLowerCase()}`);
    const valorInput = parseFloat(inputEl.value) || 0;

    const ganhoExistente = ganhos.find(g => g.responsavel === pessoa && g.mes === mes);

    if (ganhoExistente) {
        await supabaseClient.from('ganhos').update({ valor: valorInput }).eq('id', ganhoExistente.id);
    } else {
        await supabaseClient.from('ganhos').insert([{ mes: mes, responsavel: pessoa, valor: valorInput }]);
    }

    mostrarToast(`Ganho mensal de ${pessoa} atualizado para ${formatarMoeda(valorInput)}!`);
    carregarDados(false);
}

// Adicionar Conta (com Regra de Negócio: Responsável "Casal" divide por 2)
async function adicionarConta(e, pessoaOrigem) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    const valOriginal = parseFloat(formData.get('valor')) || 0;
    const responsavel = formData.get('responsavel');

    const baseConta = {
        descricao: formData.get('descricao').trim(),
        categoria: formData.get('categoria'),
        vencimento: formData.get('vencimento'),
        status: formData.get('status'),
        forma_pagamento: formData.get('forma_pagamento')
    };

    if (responsavel === 'Casal') {
        const metade = Number((valOriginal / 2).toFixed(2));
        await supabaseClient.from('contas').insert([
            { ...baseConta, valor: metade, responsavel: 'Henrique' },
            { ...baseConta, valor: metade, responsavel: 'Camila' }
        ]);
        mostrarToast(`Conta dividida! Lançado ${formatarMoeda(metade)} para Henrique e ${formatarMoeda(metade)} para Camila.`);
    } else {
        await supabaseClient.from('contas').insert([
            { ...baseConta, valor: valOriginal, responsavel: responsavel }
        ]);
        mostrarToast(`Conta "${baseConta.descricao}" adicionada para ${responsavel}!`);
    }

    form.reset();
    form.classList.add('hidden');
    carregarDados(false);
}

// Alternar Status rapidamente clicando no Badge (Pendente -> Pago -> Atrasado)
async function alternarStatusConta(id, statusAtual) {
    const ordem = ['Pendente', 'Pago', 'Atrasado'];
    const idx = ordem.indexOf(statusAtual);
    const proximoStatus = ordem[(idx + 1) % ordem.length];

    await supabaseClient.from('contas').update({ status: proximoStatus }).eq('id', id);
    mostrarToast(`Status atualizado para: ${proximoStatus}`);
    carregarDados(false);
}

// Adicionar Investimento (Calcula Saldo Atual = Valor Aplicado + Ganho no Mês)
async function adicionarInvestimento(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    const valAplicado = parseFloat(formData.get('valor_aplicado')) || 0;
    const ganhoMes = parseFloat(formData.get('ganho_mes')) || 0;
    const saldoAtual = Number((valAplicado + ganhoMes).toFixed(2));

    await supabaseClient.from('investimentos').insert([{
        data: formData.get('data'),
        responsavel: formData.get('responsavel'),
        tipo_investimento: formData.get('tipo_investimento').trim(),
        instituicao: formData.get('instituicao').trim(),
        valor_aplicado: valAplicado,
        ganho_mes: ganhoMes,
        saldo_atual: saldoAtual
    }]);

    mostrarToast(`Investimento registrado! Saldo atual: ${formatarMoeda(saldoAtual)}`);
    form.reset();
    document.getElementById('inv-preview-saldo').innerText = 'R$ 0,00';
    form.classList.add('hidden');
    carregarDados(false);
}

// Preview em tempo real do Saldo Atual no formulário de Investimentos
function atualizarPreviewSaldoInvest() {
    const val = parseFloat(document.getElementById('inv-valor-aplicado')?.value) || 0;
    const ganho = parseFloat(document.getElementById('inv-ganho-mes')?.value) || 0;
    const elPreview = document.getElementById('inv-preview-saldo');
    if (elPreview) {
        elPreview.innerText = formatarMoeda(val + ganho);
    }
}

// Excluir Registro (Conta ou Investimento)
async function deletarRegistro(tabela, id) {
    if (confirm('Tem certeza que deseja excluir este registro permanentemente?')) {
        await supabaseClient.from(tabela).delete().eq('id', id);
        mostrarToast('Registro removido com sucesso.', 'aviso');
        carregarDados(false);
    }
}

// ==========================================================================
// RENDERIZAÇÃO DE INTERFACE E GRÁFICOS
// ==========================================================================

function atualizarTelas(contasMes, investMes, ganhosMes) {
    // 1. Cálculos Consolidados do Casal
    const ganhoH = Number(ganhosMes.find(g => g.responsavel === 'Henrique')?.valor) || 0;
    const ganhoC = Number(ganhosMes.find(g => g.responsavel === 'Camila')?.valor) || 0;
    const totalEntrada = ganhoH + ganhoC;

    const totalSaida = contasMes.reduce((acc, c) => acc + Number(c.valor || 0), 0);
    const totalPagoCasal = contasMes
        .filter(c => c.status === 'Pago')
        .reduce((acc, c) => acc + Number(c.valor || 0), 0);
    const totalPendenteCasal = contasMes
        .filter(c => c.status !== 'Pago')
        .reduce((acc, c) => acc + Number(c.valor || 0), 0);

    const sobraCasal = totalEntrada - totalSaida;

    const totalInvestido = investMes.reduce((acc, i) => acc + Number(i.valor_aplicado || 0), 0);
    const totalGanhoInvest = investMes.reduce((acc, i) => acc + Number(i.ganho_mes || 0), 0);
    const totalSaldoInvest = investMes.reduce((acc, i) => acc + Number(i.saldo_atual || 0), 0);

    // 2. Atualiza Cards do Dashboard
    document.getElementById('dash-entrada').innerText = formatarMoeda(totalEntrada);
    document.getElementById('dash-entrada-detalhe').innerText =
        `Henrique: ${formatarMoeda(ganhoH)} • Camila: ${formatarMoeda(ganhoC)}`;

    document.getElementById('dash-saida').innerText = formatarMoeda(totalSaida);
    document.getElementById('dash-saida-detalhe').innerText =
        `Pago: ${formatarMoeda(totalPagoCasal)} • Pendente: ${formatarMoeda(totalPendenteCasal)}`;

    const elSobra = document.getElementById('dash-sobra');
    elSobra.innerText = formatarMoeda(sobraCasal);
    elSobra.className = `kpi-value ${sobraCasal >= 0 ? 'text-indigo-600' : 'text-rose-600'}`;

    document.getElementById('dash-investido').innerText = formatarMoeda(totalInvestido);
    document.getElementById('dash-investido-detalhe').innerText =
        `Rendimentos no mês: ${formatarMoeda(totalGanhoInvest)}`;

    // 3. Atualiza Card Comparativo lateral do Dashboard
    const saidaH = contasMes.filter(c => c.responsavel === 'Henrique').reduce((a, b) => a + Number(b.valor), 0);
    const saidaC = contasMes.filter(c => c.responsavel === 'Camila').reduce((a, b) => a + Number(b.valor), 0);
    const sobraH = ganhoH - saidaH;
    const sobraC = ganhoC - saidaC;

    document.getElementById('dash-resumo-h-gasto').innerText = formatarMoeda(saidaH);
    document.getElementById('dash-resumo-h-renda').innerText = formatarMoeda(ganhoH);
    document.getElementById('dash-resumo-h-sobra').innerText = `Sobra: ${formatarMoeda(sobraH)}`;
    document.getElementById('dash-resumo-h-sobra').className =
        `text-xs font-bold ${sobraH >= 0 ? 'text-emerald-600' : 'text-rose-600'}`;
    const percH = ganhoH > 0 ? Math.min(100, Math.round((saidaH / ganhoH) * 100)) : 0;
    document.getElementById('dash-barra-h').style.width = `${percH}%`;

    document.getElementById('dash-resumo-c-gasto').innerText = formatarMoeda(saidaC);
    document.getElementById('dash-resumo-c-renda').innerText = formatarMoeda(ganhoC);
    document.getElementById('dash-resumo-c-sobra').innerText = `Sobra: ${formatarMoeda(sobraC)}`;
    document.getElementById('dash-resumo-c-sobra').className =
        `text-xs font-bold ${sobraC >= 0 ? 'text-emerald-600' : 'text-rose-600'}`;
    const percC = ganhoC > 0 ? Math.min(100, Math.round((saidaC / ganhoC) * 100)) : 0;
    document.getElementById('dash-barra-c').style.width = `${percC}%`;

    // 4. Renderiza Gráfico de Barras por Categoria
    renderizarGraficoCategorias(contasMes);

    // 5. Renderiza Telas Individuais (Henrique e Camila)
    renderizarPessoa('Henrique', contasMes, ganhoH);
    renderizarPessoa('Camila', contasMes, ganhoC);

    // 6. Renderiza Hub de Investimentos
    renderizarInvestimentos(investMes, totalInvestido, totalGanhoInvest, totalSaldoInvest);

    // 7. Renderiza Controle Ideal
    renderizarControleIdeal(contasMes, totalEntrada, totalInvestido);
}

function renderizarGraficoCategorias(contasMes) {
    const somaCat = {};
    contasMes.forEach(c => {
        somaCat[c.categoria] = (somaCat[c.categoria] || 0) + Number(c.valor || 0);
    });

    // Ordena da maior despesa para a menor
    const entradasOrdenadas = Object.entries(somaCat).sort((a, b) => b[1] - a[1]);
    const labels = entradasOrdenadas.map(item => item[0]);
    const valores = entradasOrdenadas.map(item => Number(item[1].toFixed(2)));

    document.getElementById('badge-total-categorias').innerText = `${labels.length} categorias no mês`;

    if (grafico) grafico.destroy();
    const ctx = document.getElementById('graficoCategorias').getContext('2d');

    grafico = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.length ? labels : ['Sem despesas no mês'],
            datasets: [{
                label: 'Total na Categoria (R$)',
                data: valores.length ? valores : [0],
                backgroundColor: [
                    '#4f46e5', '#6366f1', '#ec4899', '#f43f5e',
                    '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6',
                    '#3b82f6', '#14b8a6'
                ],
                borderRadius: 8,
                maxBarThickness: 44
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    padding: 12,
                    callbacks: {
                        label: (context) => ` ${formatarMoeda(context.raw)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        callback: (val) => 'R$ ' + val.toLocaleString('pt-BR')
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function renderizarPessoa(nome, contasMes, ganhoPessoal) {
    const contasPessoa = contasMes.filter(c => c.responsavel === nome);
    const totalPagar = contasPessoa.reduce((acc, c) => acc + Number(c.valor || 0), 0);
    const totalPendente = contasPessoa
        .filter(c => c.status !== 'Pago')
        .reduce((acc, c) => acc + Number(c.valor || 0), 0);
    const sobraPessoal = ganhoPessoal - totalPagar;

    const divId = nome.toLowerCase();

    // Preenche input de Ganho Mensal
    const inputGanho = document.getElementById(`ganho-${divId}`);
    if (inputGanho) inputGanho.value = ganhoPessoal || '';

    // Renderiza os 3 Cards de Métricas Pessoais
    document.getElementById(`metricas-${divId}`).innerHTML = `
        <div class="kpi-card kpi-rose flex flex-col justify-between">
            <span class="kpi-label">Total a Pagar</span>
            <p class="kpi-value text-rose-600 mt-1">${formatarMoeda(totalPagar)}</p>
            <p class="kpi-subtext">${contasPessoa.length} lançamentos no mês</p>
        </div>
        <div class="kpi-card kpi-amber flex flex-col justify-between">
            <span class="kpi-label">Total Pendente</span>
            <p class="kpi-value text-amber-600 mt-1">${formatarMoeda(totalPendente)}</p>
            <p class="kpi-subtext">Contas ainda não pagas</p>
        </div>
        <div class="kpi-card kpi-indigo flex flex-col justify-between">
            <span class="kpi-label">Sobra Pessoal (${nome})</span>
            <p class="kpi-value ${sobraPessoal >= 0 ? 'text-indigo-600' : 'text-rose-600'} mt-1">${formatarMoeda(sobraPessoal)}</p>
            <p class="kpi-subtext">Ganho menos Total a Pagar</p>
        </div>
    `;

    // Renderiza Tabela de Histórico da Pessoa
    const tbody = document.getElementById(`tabela-${divId}`);
    if (contasPessoa.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-10 text-slate-400">
                    Nenhuma conta cadastrada para <strong>${nome}</strong> neste mês.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = contasPessoa.map(c => {
        const badgeClass =
            c.status === 'Pago'
                ? 'badge-pago'
                : c.status === 'Pendente'
                ? 'badge-pendente'
                : 'badge-atrasado';

        const dotColor =
            c.status === 'Pago'
                ? 'bg-emerald-500'
                : c.status === 'Pendente'
                ? 'bg-amber-500'
                : 'bg-rose-500';

        return `
            <tr>
                <td>
                    <div class="font-bold text-slate-900">${c.descricao}</div>
                    <div class="text-xs text-slate-500">${c.categoria}</div>
                </td>
                <td>
                    <span class="badge badge-neutral">${c.forma_pagamento || 'Pix'}</span>
                </td>
                <td class="text-slate-600 font-medium">${formatarDataBR(c.vencimento)}</td>
                <td class="font-extrabold text-slate-900">${formatarMoeda(c.valor)}</td>
                <td>
                    <button onclick="alternarStatusConta('${c.id}', '${c.status}')" title="Clique para alternar o status" class="badge ${badgeClass} cursor-pointer hover:opacity-80 transition">
                        <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
                        <span>${c.status}</span>
                    </button>
                </td>
                <td class="text-right">
                    <button onclick="abrirModalEditarConta('${c.id}')" title="Editar conta" class="p-2 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition">✏️</button>
                    <button onclick="deletarRegistro('contas', '${c.id}')" title="Excluir conta" class="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarInvestimentos(investMes, totalInvestido, totalGanhoInvest, totalSaldoInvest) {
    document.getElementById('inv-total-aplicado').innerText = formatarMoeda(totalInvestido);
    document.getElementById('inv-total-ganho').innerText = formatarMoeda(totalGanhoInvest);
    document.getElementById('inv-saldo-atual').innerText = formatarMoeda(totalSaldoInvest);

    const rentabilidade = totalSaldoInvest > 0 ? ((totalGanhoInvest / totalSaldoInvest) * 100).toFixed(2) : '0.00';
    document.getElementById('inv-rentabilidade-media').innerText = `Rentabilidade no mês: ${rentabilidade.replace('.', ',')}%`;

    const tbInvest = document.getElementById('tabela-invest');
    if (investMes.length === 0) {
        tbInvest.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-10 text-slate-400">
                    Nenhum aporte cadastrado neste mês. Clique em <strong>+ Novo Aporte</strong> para registrar.
                </td>
            </tr>
        `;
        return;
    }

    tbInvest.innerHTML = investMes.map(i => `
        <tr>
            <td class="text-slate-600 font-medium">${formatarDataBR(i.data)}</td>
            <td><span class="badge badge-neutral">${i.responsavel}</span></td>
            <td>
                <div class="font-bold text-slate-900">${i.tipo_investimento}</div>
                <div class="text-xs text-slate-500">${i.instituicao}</div>
            </td>
            <td class="font-bold text-slate-800">${formatarMoeda(i.valor_aplicado)}</td>
            <td class="font-bold text-emerald-600">+ ${formatarMoeda(i.ganho_mes)}</td>
            <td class="font-extrabold text-violet-700">${formatarMoeda(i.saldo_atual)}</td>
            <td class="text-right">
                <button onclick="deletarRegistro('investimentos', '${i.id}')" title="Excluir investimento" class="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');
}

// ==========================================================================
// GERAÇÃO DINÂMICA DO FORMULÁRIO DE CONTAS (COM PREVIEW DE DIVISÃO CASAL)
// ==========================================================================

function gerarFormConta(formId, pessoaDefault) {
    const form = document.getElementById(formId);
    const sufixo = pessoaDefault.toLowerCase();

    form.innerHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div class="sm:col-span-2">
                <label class="form-label">Descrição da Conta</label>
                <input type="text" name="descricao" placeholder="Ex: Aluguel, Cemig, Supermercado..." required class="form-input">
            </div>
            <div>
                <label class="form-label">Categoria</label>
                <select name="categoria" class="form-input">
                    ${categorias.map(c => `<option value="${c}">${c}</option>`).join('')}
                </select>
            </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-4">
            <div>
                <label class="form-label">Valor Total (R$)</label>
                <input type="number" name="valor" id="valor-${sufixo}" placeholder="0,00" step="0.01" required class="form-input" oninput="atualizarAvisoCasal('${sufixo}')">
            </div>
            <div>
                <label class="form-label">Data de Vencimento</label>
                <input type="date" name="vencimento" value="2026-11-10" required class="form-input">
            </div>
            <div>
                <label class="form-label">Status</label>
                <select name="status" class="form-input">
                    ${statusList.map(s => `<option value="${s}">${s}</option>`).join('')}
                </select>
            </div>
            <div>
                <label class="form-label">Forma de Pagamento</label>
                <select name="forma_pagamento" class="form-input">
                    ${formasPagamento.map(f => `<option value="${f}">${f}</option>`).join('')}
                </select>
            </div>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-4 pt-2">
            <div class="w-full sm:w-72">
                <label class="form-label">Responsável pelo Pagamento</label>
                <select name="responsavel" id="resp-${sufixo}" class="form-input font-semibold" onchange="atualizarAvisoCasal('${sufixo}')">
                    <option value="Henrique" ${pessoaDefault === 'Henrique' ? 'selected' : ''}>👨 Individual: Henrique</option>
                    <option value="Camila" ${pessoaDefault === 'Camila' ? 'selected' : ''}>👩 Individual: Camila</option>
                    <option value="Casal">💍 Casal (Dividir 50% / 50%)</option>
                </select>
            </div>

            <div id="aviso-casal-${sufixo}" class="hidden text-xs font-bold text-indigo-700 bg-indigo-100/80 border border-indigo-200 px-3.5 py-2 rounded-xl">
                💡 Divisão automática: R$ 0,00 para Henrique e R$ 0,00 para Camila.
            </div>

            <div class="flex gap-2 ml-auto">
                <button type="button" onclick="toggleForm('${formId}')" class="btn-secondary">Cancelar</button>
                <button type="submit" class="btn-primary px-6">Salvar Lançamento</button>
            </div>
        </div>
    `;
}

function atualizarAvisoCasal(sufixo) {
    const selectResp = document.getElementById(`resp-${sufixo}`);
    const inputValor = document.getElementById(`valor-${sufixo}`);
    const aviso = document.getElementById(`aviso-casal-${sufixo}`);

    if (!selectResp || !aviso) return;

    if (selectResp.value === 'Casal') {
        const metade = (parseFloat(inputValor.value) || 0) / 2;
        aviso.innerText = `💡 Divisão 50/50: Lançará ${formatarMoeda(metade)} para Henrique e ${formatarMoeda(metade)} para Camila.`;
        aviso.classList.remove('hidden');
    } else {
        aviso.classList.add('hidden');
    }
}

// ==========================================================================
// CONTROLE IDEAL (REGRA 50 / 30 / 10 / 5)
// ==========================================================================

const PILARES_IDEAL = [
    { chave: 'fixos', titulo: 'Gastos Fixos', icone: '🏠', perc: 0.50, tipo: 'teto',
      categorias: ['Moradia', 'Mercado', 'Transporte', 'Saúde', 'Telefone', 'Energia', 'Água'] },
    { chave: 'variaveis', titulo: 'Gastos Variáveis', icone: '💳', perc: 0.30, tipo: 'teto',
      categorias: ['Cartão de crédito', 'Financiamento'] },
    { chave: 'lazer', titulo: 'Lazer', icone: '🎉', perc: 0.10, tipo: 'teto', categorias: ['Lazer'] },
    { chave: 'invest', titulo: 'Investimentos & Sonhos', icone: '🚀', perc: 0.05, tipo: 'meta', categorias: [] }
];

function renderizarControleIdeal(contasMes, rendaTotal, totalInvestido) {
    const elRenda = document.getElementById('ci-renda');
    const container = document.getElementById('ci-cards');
    if (!elRenda || !container) return;
    elRenda.innerText = formatarMoeda(rendaTotal);

    container.innerHTML = PILARES_IDEAL.map(p => {
        const gasto = p.tipo === 'meta'
            ? totalInvestido
            : contasMes.filter(c => p.categorias.includes(c.categoria)).reduce((a, c) => a + Number(c.valor || 0), 0);
        const ideal = rendaTotal * p.perc;
        // Teto: resultado positivo = sobrou dentro do limite. Meta: positivo = superou a meta.
        const resultado = p.tipo === 'meta' ? gasto - ideal : ideal - gasto;
        const ok = p.tipo === 'meta' ? gasto >= ideal && (rendaTotal > 0 || gasto > 0) : gasto <= ideal;
        const percReal = rendaTotal > 0 ? (gasto / rendaTotal) * 100 : 0;
        const sinal = resultado >= 0 ? '+' : '-';
        const cor = ok ? 'emerald' : 'rose';
        const alerta = ok
            ? (p.tipo === 'meta' ? '✅ Meta mínima atingida' : '✅ Dentro do limite ideal')
            : (p.tipo === 'meta' ? '⚠️ Abaixo da meta mínima de 5%' : `⚠️ Alerta: acima do teto de ${p.perc * 100}%`);
        const barra = rendaTotal > 0 ? Math.min(100, (gasto / (ideal || 1)) * 100) : 0;
        return `
        <div class="surface-card p-5 border-l-4 ${ok ? 'border-l-emerald-500' : 'border-l-rose-500'}">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">${p.icone}</span>
                    <div>
                        <h4 class="font-bold text-slate-900 text-sm">${p.titulo}</h4>
                        <p class="text-[11px] text-slate-400">${p.tipo === 'meta' ? 'Meta mínima' : 'Limite máximo'}: ${p.perc * 100}% da renda</p>
                    </div>
                </div>
                <span class="text-xs font-bold px-2 py-1 rounded-lg bg-${cor}-50 text-${cor}-600">${percReal.toFixed(1).replace('.', ',')}%</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-xs mb-3">
                <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200/70">
                    <p class="text-slate-400 font-semibold">Gasto mês</p>
                    <p class="font-bold text-slate-800 mt-0.5">${formatarMoeda(gasto)}</p>
                </div>
                <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200/70">
                    <p class="text-slate-400 font-semibold">Gasto ideal mês</p>
                    <p class="font-bold text-slate-800 mt-0.5">${formatarMoeda(ideal)}</p>
                </div>
                <div class="p-2.5 rounded-xl bg-${cor}-50 border border-${cor}-200">
                    <p class="text-${cor}-600 font-semibold">Resultado mês</p>
                    <p class="font-extrabold text-${cor}-600 mt-0.5">${sinal} ${formatarMoeda(Math.abs(resultado))}</p>
                </div>
            </div>
            <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden mb-2">
                <div class="bg-${cor}-500 h-full rounded-full transition-all duration-500" style="width:${barra}%"></div>
            </div>
            <p class="text-xs font-bold text-${cor}-600">${alerta}</p>
        </div>`;
    }).join('');
}

// ==========================================================================
// DÍVIDAS (ABA ISOLADA — NÃO IMPACTA OUTROS CÁLCULOS)
// ==========================================================================

const STATUS_DIVIDA = ['Pendente', 'Pagando', 'Negociada', 'Caducar!', 'Paga'];
const COR_STATUS_DIVIDA = {
    'Paga': 'bg-emerald-50 text-emerald-700 border-emerald-200',
    'Negociada': 'bg-sky-50 text-sky-700 border-sky-200',
    'Pagando': 'bg-amber-50 text-amber-700 border-amber-200',
    'Caducar!': 'bg-slate-100 text-slate-600 border-slate-300',
    'Pendente': 'bg-rose-50 text-rose-700 border-rose-200'
};

const escaparHTML = (t) => String(t ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

async function carregarDividas() {
    const { data, error } = await supabaseClient.from('dividas').select('*').order('data_inicio', { ascending: false });
    if (error) {
        console.error('Erro ao carregar dívidas:', error);
        return;
    }
    dividas = data || [];
    renderizarDividas();
}

async function adicionarDivida(e) {
    e.preventDefault();
    const form = e.target;
    const fd = new FormData(form);
    const { error } = await supabaseClient.from('dividas').insert([{
        descricao: fd.get('descricao').trim(),
        data_inicio: fd.get('data_inicio'),
        valor_inicial: parseFloat(fd.get('valor_inicial')) || 0,
        valor_total: parseFloat(fd.get('valor_total')) || 0,
        responsavel: fd.get('responsavel'),
        status: fd.get('status')
    }]);
    if (error) return mostrarToast('Erro ao salvar dívida: ' + error.message, 'erro');
    mostrarToast('Dívida cadastrada com sucesso!');
    form.reset();
    form.classList.add('hidden');
    carregarDividas();
}

async function alterarStatusDivida(id, novoStatus) {
    const { error } = await supabaseClient.from('dividas').update({ status: novoStatus }).eq('id', id);
    if (error) return mostrarToast('Erro ao atualizar status: ' + error.message, 'erro');
    mostrarToast(`Status atualizado para "${novoStatus}"`);
    carregarDividas();
}

async function deletarDivida(id) {
    if (!confirm('Tem certeza que deseja excluir esta dívida permanentemente?')) return;
    const { error } = await supabaseClient.from('dividas').delete().eq('id', id);
    if (error) return mostrarToast('Erro ao excluir: ' + error.message, 'erro');
    mostrarToast('Dívida removida.', 'aviso');
    carregarDividas();
}

function renderizarDividas() {
    ['Henrique', 'Camila'].forEach(nome => {
        const p = nome.toLowerCase();
        const lista = dividas.filter(d => d.responsavel === nome);
        const total = lista.reduce((a, d) => a + Number(d.valor_total || 0), 0);
        const inicial = lista.reduce((a, d) => a + Number(d.valor_inicial || 0), 0);

        document.getElementById(`div-total-${p}`).innerText = formatarMoeda(total);
        document.getElementById(`div-inicial-${p}`).innerText = `Valor inicial somado: ${formatarMoeda(inicial)}`;
        document.getElementById(`div-qtd-${p}`).innerText = `${lista.length} ${lista.length === 1 ? 'dívida' : 'dívidas'}`;

        const tbody = document.getElementById(`div-tabela-${p}`);
        if (lista.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-xs text-slate-400">Nenhuma dívida cadastrada.</td></tr>`;
            return;
        }
        tbody.innerHTML = lista.map(d => `
            <tr class="border-b border-slate-100 last:border-0">
                <td class="py-2.5 pr-3 font-semibold text-slate-800">${escaparHTML(d.descricao)}</td>
                <td class="py-2.5 pr-3 text-slate-500 whitespace-nowrap">${formatarDataBR(d.data_inicio)}</td>
                <td class="py-2.5 pr-3 text-right text-slate-500 whitespace-nowrap">${formatarMoeda(d.valor_inicial)}</td>
                <td class="py-2.5 pr-3 text-right font-bold text-slate-800 whitespace-nowrap">${formatarMoeda(d.valor_total)}</td>
                <td class="py-2.5 pr-3">
                    <select onchange="alterarStatusDivida('${d.id}', this.value)" class="text-xs font-bold rounded-lg border px-2 py-1 cursor-pointer ${COR_STATUS_DIVIDA[d.status] || COR_STATUS_DIVIDA.Pendente}">
                        ${STATUS_DIVIDA.map(s => `<option value="${s}" ${s === d.status ? 'selected' : ''}>${s}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 text-right">
                    <button onclick="deletarDivida('${d.id}')" title="Excluir dívida" class="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition">🗑️</button>
                </td>
            </tr>`).join('');
    });
}


// ==========================================================================
// EDIÇÃO DE CONTAS
// ==========================================================================

function abrirModalEditarConta(id) {
    const c = contas.find(x => String(x.id) === String(id));
    if (!c) { mostrarToast('Conta não encontrada.', 'erro'); return; }
    const opts = (lista, atual) => {
        const l = lista.includes(atual) || !atual ? lista : [atual, ...lista];
        return l.map(v => `<option value="${v}" ${v === atual ? 'selected' : ''}>${v}</option>`).join('');
    };
    document.getElementById('edit-id').value = c.id;
    document.getElementById('edit-descricao').value = c.descricao || '';
    document.getElementById('edit-categoria').innerHTML = opts(categorias, c.categoria);
    document.getElementById('edit-valor').value = Number(c.valor || 0).toFixed(2);
    document.getElementById('edit-vencimento').value = (c.vencimento || '').slice(0, 10);
    document.getElementById('edit-status').innerHTML = opts(statusList, c.status);
    document.getElementById('edit-forma').innerHTML = opts(formasPagamento, c.forma_pagamento || 'Pix');
    document.getElementById('edit-responsavel').value = c.responsavel || 'Henrique';
    document.getElementById('modal-editar-conta').classList.remove('hidden');
}

function fecharModalEditarConta() {
    document.getElementById('modal-editar-conta').classList.add('hidden');
}

async function salvarEdicaoConta(event) {
    event.preventDefault();
    const contaId = document.getElementById('edit-id').value;
    const dados = {
        descricao: document.getElementById('edit-descricao').value.trim(),
        categoria: document.getElementById('edit-categoria').value,
        valor: Number(parseFloat(document.getElementById('edit-valor').value).toFixed(2)),
        vencimento: document.getElementById('edit-vencimento').value,
        status: document.getElementById('edit-status').value,
        forma_pagamento: document.getElementById('edit-forma').value,
        responsavel: document.getElementById('edit-responsavel').value
    };
    const { error } = await supabaseClient.from('contas').update(dados).eq('id', contaId);
    if (error) {
        console.error(error);
        mostrarToast('Erro ao atualizar a conta. Tente novamente.', 'erro');
        return;
    }
    fecharModalEditarConta();
    mostrarToast('Conta atualizada com sucesso!');
    carregarDados(false);
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') fecharModalEditarConta(); });
