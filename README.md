<div align="center">
  <style>
    @keyframes pulse {
      0% { opacity: 0.8; text-shadow: 0 0 5px #00ff41; }
      50% { opacity: 1; text-shadow: 0 0 20px #00ff41, 0 0 40px #008000; }
      100% { opacity: 0.8; text-shadow: 0 0 5px #00ff41; }
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
    
    @keyframes rain {
      0% { background-position: 0 0; }
      100% { background-position: 0 20px; }
    }
    
    .matrix-bg {
      background: linear-gradient(180deg, #0d0208 0%, #1a0f1a 100%);
      padding: 40px 20px;
      border-radius: 20px;
      border: 1px solid #00ff41;
      box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
      position: relative;
      overflow: hidden;
    }
    
    .matrix-bg::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: repeating-linear-gradient(
        0deg,
        rgba(0, 255, 65, 0.03) 0px,
        rgba(0, 255, 65, 0.1) 1px,
        transparent 1px,
        transparent 2px
      );
      pointer-events: none;
      animation: rain 20s linear infinite;
    }
    
    .glitch {
      font-size: 5em;
      font-weight: 900;
      font-family: 'Courier New', monospace;
      color: #00ff41;
      text-shadow: 
        3px 3px 0 #ff00ff,
        -3px -3px 0 #00ffff;
      animation: pulse 2s infinite;
      letter-spacing: 5px;
      margin: 20px 0;
      position: relative;
    }
    
    .glitch::before,
    .glitch::after {
      content: "КАТАЛОГ AI";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .glitch::before {
      color: #ff00ff;
      z-index: -1;
      transform: translate(-2px, -2px);
    }
    
    .glitch::after {
      color: #00ffff;
      z-index: -2;
      transform: translate(2px, 2px);
    }
    
    .terminal {
      background: rgba(0, 0, 0, 0.8);
      border: 1px solid #00ff41;
      border-radius: 10px;
      padding: 20px;
      margin: 30px auto;
      max-width: 600px;
      text-align: left;
      font-family: 'Courier New', monospace;
      color: #00ff41;
      box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
    }
    
    .terminal-line {
      margin: 5px 0;
      white-space: nowrap;
      overflow: hidden;
      animation: typing 3s steps(40);
    }
    
    .terminal-line::before {
      content: "$ ";
      color: #ff00ff;
    }
    
    .cursor {
      animation: blink 1s infinite;
      background: #00ff41;
      width: 10px;
      height: 20px;
      display: inline-block;
      margin-left: 5px;
    }
    
    .badge-matrix {
      display: inline-block;
      padding: 10px 25px;
      margin: 10px;
      background: transparent;
      border: 2px solid #00ff41;
      color: #00ff41;
      font-family: 'Courier New', monospace;
      font-weight: bold;
      text-decoration: none;
      border-radius: 5px;
      transition: all 0.3s;
      box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }
    
    .badge-matrix:hover {
      background: #00ff41;
      color: #0d0208;
      box-shadow: 0 0 30px #00ff41;
      transform: scale(1.05);
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin: 40px 0;
    }
    
    .stat-item {
      background: rgba(0, 255, 65, 0.05);
      border: 1px solid #00ff41;
      padding: 20px;
      border-radius: 10px;
      font-family: 'Courier New', monospace;
    }
    
    .stat-number {
      font-size: 2.5em;
      color: #00ff41;
      font-weight: bold;
    }
    
    .stat-label {
      color: #00ff99;
      font-size: 0.9em;
      text-transform: uppercase;
    }
    
    @media (max-width: 600px) {
      .glitch { font-size: 2.5em; }
      .stats-grid { grid-template-columns: 1fr; }
    }
  </style>

  <div class="matrix-bg">
    <!-- ASCII дождь вверху -->
    <pre style="color: #00ff41; opacity: 0.3; font-size: 10px; line-height: 10px; margin: -20px 0 -10px 0;">
01001110 01100101 01110100 01110010 01101111 01101110
    </pre>

    <!-- Главный заголовок с глитч-эффектом -->
    <div class="glitch">
      КАТАЛОГ AI
    </div>

    <!-- Подзаголовок -->
    <div style="color: #00ff99; font-family: 'Courier New'; font-size: 1.2em; margin: 10px 0;">
      &lt;ACCESS_PRIVILEGES = GRANTED&gt;
    </div>

    <!-- Терминал -->
    <div class="terminal">
      <div class="terminal-line">system.init()...</div>
      <div class="terminal-line">loading neural_networks.db...</div>
      <div class="terminal-line">found 1,247 active AI tools</div>
      <div class="terminal-line">categorizing... 53 categories detected</div>
      <div class="terminal-line">status: <span style="color: #ff00ff;">ONLINE</span><span class="cursor"></span></div>
    </div>

    <!-- Статистика -->
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-number">1,247+</div>
        <div class="stat-label">> нейросетей</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">53</div>
        <div class="stat-label">> категорий</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">24/7</div>
        <div class="stat-label">> обновление</div>
      </div>
    </div>

    <!-- Кнопки -->
    <div style="margin: 30px 0;">
      <a href="#" class="badge-matrix">[ ПРОНИКНУТЬ ]</a>
      <a href="#" class="badge-matrix">[ ДОКУМЕНТАЦИЯ ]</a>
      <a href="#" class="badge-matrix">[ API ]</a>
    </div>

    <!-- Матричный код внизу -->
    <pre style="color: #00ff41; opacity: 0.2; font-size: 8px; line-height: 8px; margin: 20px 0 -30px 0;">
1001001 01001110 01001001 01010100 01001001 01000001 01001100 01001001 01011010 01000101
    </pre>
  </div>
</div>

<!-- Огромные отступы, чтобы спрятать список файлов -->
<br><br><br><br><br><br><br><br><br><br><br><br>
<br><br><br><br><br><br><br><br><br><br><br><br>
<br><br><br><br><br><br><br><br><br><br><br><br>
<br><br><br><br><br><br><br><br><br><br><br><br>
