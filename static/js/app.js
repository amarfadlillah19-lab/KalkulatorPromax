document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentCategory = 'aritmatika';
    let currentOperation = null;
    let isDark = true;

    // Elements
    const tabs = document.querySelectorAll('.tab-btn');
    const navBtns = document.querySelectorAll('.nav-btn[data-cat]');
    const opsGrids = document.querySelectorAll('.ops-grid');
    const opBtns = document.querySelectorAll('.op-btn');
    const btnHitung = document.getElementById('btnHitung');
    const btnClear = document.getElementById('btnClear');
    const themeToggle = document.getElementById('themeToggle');
    const inputA = document.getElementById('inputA');
    const inputB = document.getElementById('inputB');
    const inputSingle = document.getElementById('inputSingle');
    const dualInput = document.getElementById('dualInput');
    const singleInput = document.getElementById('singleInput');
    const consoleBody = document.getElementById('consoleBody');
    const logsBody = document.getElementById('logsBody');
    const windowTitle = document.getElementById('windowTitle');
    const sessionDate = document.getElementById('sessionDate');

    // Set session date
    const now = new Date();
    sessionDate.textContent = `# Session started: ${now.toISOString().split('T')[0]}`;

    // Theme handling
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        isDark = false;
        document.documentElement.setAttribute('data-theme', 'light');
    }

    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        if (isDark) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // Category mapping for titles
    const catTitles = {
        'aritmatika': 'Arithmetic.exe',
        'logika': 'Logic.exe',
        'basis': 'BasisConverter.exe',
        'suhu': 'TempConverter.exe',
        'kurs': 'Currency.exe',
        'bonus': 'BonusTools.exe'
    };

    // Single input categories
    const singleInputCats = ['basis', 'suhu', 'kurs', 'bonus'];

    // Switch category function
    function switchCategory(cat) {
        currentCategory = cat;
        currentOperation = null;

        // Update tabs
        tabs.forEach(t => {
            t.classList.toggle('active', t.dataset.cat === cat);
        });

        // Update nav
        navBtns.forEach(n => {
            n.classList.toggle('active', n.dataset.cat === cat);
        });

        // Update ops grids
        opsGrids.forEach(g => {
            g.classList.toggle('active', g.dataset.cat === cat);
        });

        // Update window title
        windowTitle.textContent = catTitles[cat] || 'Kalkulator.exe';

        // Toggle inputs
        if (singleInputCats.includes(cat)) {
            dualInput.classList.add('d-none');
            singleInput.classList.remove('d-none');
        } else {
            dualInput.classList.remove('d-none');
            singleInput.classList.add('d-none');
        }

        // Clear op selection
        opBtns.forEach(b => b.classList.remove('selected'));

        // Clear console
        clearConsole();
    }

    // Tab click handlers
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchCategory(tab.dataset.cat));
    });

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => switchCategory(btn.dataset.cat));
    });

    // Operation button handlers
    opBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const parent = btn.closest('.ops-grid');
            if (!parent.classList.contains('active')) return;

            parent.querySelectorAll('.op-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            currentOperation = btn.dataset.op;
        });
    });

    // Console functions
    function clearConsole() {
        consoleBody.innerHTML = '<div class="console-line">> HASIL: 0</div><div class="console-line blink">_</div>';
    }

    function writeConsole(text, isResult = false) {
        consoleBody.innerHTML = '';
        const lines = text.split('\n');
        lines.forEach(line => {
            const div = document.createElement('div');
            div.className = 'console-line';
            div.textContent = '> ' + line;
            if (isResult) div.style.color = '#4ade80';
            consoleBody.appendChild(div);
        });
        const blink = document.createElement('div');
        blink.className = 'console-line blink';
        blink.textContent = '_';
        consoleBody.appendChild(blink);

        // Auto scroll
        consoleBody.scrollTop = consoleBody.scrollHeight;
    }

    // Logs functions
    function addLog(formula, result) {
        const time = new Date().toLocaleTimeString('id-ID', {hour12: false});
        const logLine = document.createElement('div');
        logLine.className = 'log-line';
        logLine.innerHTML = `<span class="timestamp">[${time}]</span> ${formula} = ${result}`;
        logsBody.insertBefore(logLine, logsBody.firstChild);

        // Keep max 50 logs in DOM
        while (logsBody.children.length > 50) {
            logsBody.removeChild(logsBody.lastChild);
        }
    }

    function clearLogs() {
        logsBody.innerHTML = '<div class="log-line">> _</div>';
        fetch('/clear-history', {method: 'POST'});
    }

    btnClear.addEventListener('click', clearLogs);

    // Calculate
    btnHitung.addEventListener('click', async () => {
        if (!currentOperation) {
            writeConsole('ERROR: Pilih operasi terlebih dahulu!');
            return;
        }

        let payload = {
            category: currentCategory,
            operation: currentOperation
        };

        if (singleInputCats.includes(currentCategory)) {
            const val = document.getElementById('inputSingle').value;
            if (val === '') {
                writeConsole('ERROR: Input tidak boleh kosong!');
                return;
            }
            payload.value = val;
        } else {
            const a = inputA.value;
            const b = inputB.value;
            if (a === '' || (currentOperation !== 'NOT' && currentOperation !== 'sqrt' && b === '')) {
                writeConsole('ERROR: Input tidak lengkap!');
                return;
            }
            payload.a = a;
            payload.b = b;
        }

        // Special case for sqrt and NOT - only need A
        if (currentOperation === 'sqrt' || currentOperation === 'NOT') {
            payload.b = '0';
        }

        try {
            btnHitung.textContent = '[ MEMPROSES... ]';
            btnHitung.disabled = true;

            const res = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (data.error) {
                writeConsole(`ERROR: ${data.error}`);
            } else {
                // Format output
                let output = '';
                output += `RUMUS: ${data.formula}\n`;
                output += `HASIL: ${data.result}\n`;
                output += '--- LANGKAH ---\n';
                data.steps.forEach((step, i) => {
                    output += `${i+1}. ${step}\n`;
                });
                writeConsole(output, true);
                addLog(data.formula, data.result);
            }
        } catch (err) {
            writeConsole(`ERROR: ${err.message}`);
        } finally {
            btnHitung.textContent = '[ HITUNG ]';
            btnHitung.disabled = false;
        }
    });

    // Enter key handler
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            btnHitung.click();
        }
    });

    // Load history on startup
    async function loadHistory() {
        try {
            const res = await fetch('/history');
            const data = await res.json();
            if (data.history && data.history.length > 0) {
                logsBody.innerHTML = '';
                data.history.forEach(item => {
                    const time = new Date().toLocaleTimeString('id-ID', {hour12: false});
                    const logLine = document.createElement('div');
                    logLine.className = 'log-line';
                    logLine.innerHTML = `<span class="timestamp">[${time}]</span> ${item.formula} = ${item.result}`;
                    logsBody.appendChild(logLine);
                });
            }
        } catch (e) {
            console.log('History load failed', e);
        }
    }

    loadHistory();

    // Init
    switchCategory('aritmatika');
});