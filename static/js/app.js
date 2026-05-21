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
