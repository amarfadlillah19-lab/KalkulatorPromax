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