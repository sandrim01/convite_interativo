// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'sucesso') {
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao ${tipo}`;
    notificacao.innerHTML = `
        <i class="fas ${tipo === 'sucesso' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${mensagem}</span>
    `;
    
    // Adicionar estilos
    notificacao.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${tipo === 'sucesso' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notificacao);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notificacao.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notificacao);
        }, 300);
    }, 3000);
}

// Adicionar animações CSS dinamicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Função para validar formulários
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let valido = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#dc3545';
            valido = false;
        } else {
            input.style.borderColor = '#e0e0e0';
        }
    });
    
    return valido;
}

// Função para formatar moeda
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Função para aplicar máscara de telefone
function mascaraTelefone(input) {
    let valor = input.value.replace(/\D/g, '');
    
    if (valor.length <= 10) {
        valor = valor.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    } else {
        valor = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    
    input.value = valor;
}

// Aplicar máscara de telefone automaticamente
document.addEventListener('DOMContentLoaded', function() {
    const telefoneInputs = document.querySelectorAll('input[type="tel"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            mascaraTelefone(this);
        });
    });
});

// Função para smooth scroll
function scrollSuave(elemento) {
    elemento.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Função para detectar se o elemento está visível
function estaVisivel(elemento) {
    const rect = elemento.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Função para animar elementos quando ficam visíveis
function animarElementosVisiveis() {
    const elementos = document.querySelectorAll('.animate-on-scroll');
    
    elementos.forEach(elemento => {
        if (estaVisivel(elemento)) {
            elemento.classList.add('animated');
        }
    });
}

// Observador de intersecção para animações
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, {
    threshold: 0.1
});

// Aplicar observador aos cards de presente
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.presente-card');
    cards.forEach(card => {
        observer.observe(card);
    });
});

// Função para copiar link para área de transferência
function copiarLink(url) {
    navigator.clipboard.writeText(url).then(() => {
        mostrarNotificacao('Link copiado para a área de transferência!');
    }).catch(() => {
        mostrarNotificacao('Erro ao copiar link', 'erro');
    });
}

// Função para compartilhar convite
function compartilharConvite() {
    if (navigator.share) {
        navigator.share({
            title: 'Convite de Casamento - Alessandro & [Nome da Noiva]',
            text: 'Você está convidado(a) para nosso casamento!',
            url: window.location.href
        });
    } else {
        copiarLink(window.location.href);
    }
}

// Função para salvar data no calendário
function salvarNoCalendario() {
    const evento = {
        title: 'Casamento Alessandro & [Nome da Noiva]',
        start: '2024-09-15T18:00:00',
        end: '2024-09-15T23:00:00',
        description: 'Cerimônia de casamento',
        location: 'Igreja São José, Rua das Flores, 123 - Centro, São Paulo - SP'
    };
    
    const startDate = new Date(evento.start);
    const endDate = new Date(evento.end);
    
    const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(evento.title)}&dates=${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z/${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z&details=${encodeURIComponent(evento.description)}&location=${encodeURIComponent(evento.location)}`;
    
    window.open(googleCalendarUrl, '_blank');
}

// Função para verificar conexão com internet
function verificarConexao() {
    if (!navigator.onLine) {
        mostrarNotificacao('Sem conexão com a internet. Algumas funcionalidades podem não funcionar.', 'erro');
    }
}

// Verificar conexão ao carregar a página
document.addEventListener('DOMContentLoaded', verificarConexao);

// Verificar mudanças na conexão
window.addEventListener('online', () => {
    mostrarNotificacao('Conexão restaurada!');
});

window.addEventListener('offline', () => {
    mostrarNotificacao('Conexão perdida. Trabalhando offline.', 'erro');
});

// Função para loading
function mostrarLoading(elemento) {
    elemento.disabled = true;
    elemento.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
}

function esconderLoading(elemento, textoOriginal) {
    elemento.disabled = false;
    elemento.innerHTML = textoOriginal;
}

// Debounce para otimizar performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Função para lazy loading de imagens
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Inicializar lazy loading ao carregar a página
document.addEventListener('DOMContentLoaded', lazyLoadImages);

// Função para analytics simples (opcional)
function trackEvent(categoria, acao, label) {
    // Implementar tracking aqui se necessário
    console.log(`Event tracked: ${categoria} - ${acao} - ${label}`);
}

// Exportar funções para uso global
window.ConviteUtils = {
    mostrarNotificacao,
    validarFormulario,
    formatarMoeda,
    mascaraTelefone,
    scrollSuave,
    copiarLink,
    compartilharConvite,
    salvarNoCalendario,
    mostrarLoading,
    esconderLoading,
    trackEvent
};
