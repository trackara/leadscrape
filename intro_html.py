INTRO_HTML = """
<script>
(function() {
  // Escape Streamlit's iframe and inject overlay into the real page
  var doc = window.parent.document;

  if (doc.getElementById('sc-intro-overlay')) return;

  // Inject Google Fonts into parent
  var link = doc.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&display=swap';
  doc.head.appendChild(link);

  // Inject styles into parent
  var style = doc.createElement('style');
  style.textContent = `
    @keyframes sc-spin   { from{transform:rotate(0)}   to{transform:rotate(360deg)} }
    @keyframes sc-spinR  { from{transform:rotate(0)}   to{transform:rotate(-360deg)} }
    @keyframes sc-pulse  { 0%,100%{transform:scale(1)} 50%{transform:scale(1.04)} }
    @keyframes sc-bar    { from{width:0} to{width:68%} }
    @keyframes sc-dot    { 0%,100%{opacity:.12;transform:scale(.5)} 50%{opacity:.75;transform:scale(1.2)} }
    @keyframes sc-fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
    @keyframes sc-fadeIn { from{opacity:0} to{opacity:1} }
    @keyframes sc-lineG  { from{transform:scaleX(0)} to{transform:scaleX(1)} }
    @keyframes sc-sealIn { from{opacity:0;transform:scale(.72) rotate(-12deg)} to{opacity:1;transform:scale(1) rotate(0)} }
    @keyframes sc-cardIn { from{opacity:0;transform:translateX(36px) translateY(18px)} to{opacity:1;transform:translateX(0) translateY(0)} }
    @keyframes sc-logoIn { from{opacity:0;filter:blur(10px);transform:scale(.82)} to{opacity:1;filter:blur(0);transform:scale(1)} }
    @keyframes sc-out    { from{opacity:1;transform:scale(1)} to{opacity:0;transform:scale(.985)} }

    #sc-intro-overlay {
      position:fixed;inset:0;z-index:2147483647;
      background:#0f0f0d;
      font-family:'DM Sans',sans-serif;
      display:flex;align-items:center;justify-content:center;
      transition:opacity .9s ease,transform .9s ease;
    }
    #sc-intro-overlay.sc-out { animation:sc-out .9s ease forwards; }

    .sc-card {
      position:relative;overflow:hidden;border-radius:24px;
      background:linear-gradient(135deg,#132118 0%,#223727 55%,#74664a 100%);
      width:min(96vw,1200px);min-height:min(86vh,640px);
      display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:52px;
      box-shadow:0 40px 120px rgba(0,0,0,.7);
    }
    .sc-bloom {
      position:absolute;inset:0;pointer-events:none;
      background:radial-gradient(circle at 28% 18%,rgba(255,255,255,.18),transparent 28%),
                 radial-gradient(circle at 82% 4%,rgba(255,255,255,.10),transparent 20%);
    }
    .sc-dot { position:absolute;border-radius:50%;animation:sc-dot 3s ease-in-out infinite }
    .sc-hline { position:absolute;height:1px;transform-origin:left;animation:sc-lineG 1.5s ease forwards }
    .sc-badge { display:inline-flex;align-items:center;gap:8px;border-radius:99px;padding:7px 16px;font-size:10px;letter-spacing:.26em;text-transform:uppercase;border:1px solid rgba(255,255,255,.22);color:rgba(255,255,255,.72);animation:sc-fadeUp .5s ease .25s both }
    .sc-eyebrow { margin-top:34px;font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:rgba(247,237,220,.52);animation:sc-fadeUp .5s ease .55s both }
    .sc-h1 { margin-top:16px;font-family:'DM Serif Display',serif;font-size:clamp(2rem,3.5vw,3.8rem);line-height:.94;color:#F7EDDC;max-width:500px;animation:sc-fadeUp .9s ease .75s both }
    .sc-by { margin-top:18px;font-size:13px;color:rgba(255,255,255,.48);animation:sc-fadeIn .5s ease 1.1s both }
    .sc-stats { margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;animation:sc-fadeUp .8s ease 1.4s both }
    .sc-stat { border-radius:16px;padding:16px;backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.10) }
    .sc-sym { font-size:20px;color:#9BA66B;margin-bottom:14px }
    .sc-val { font-size:22px;font-weight:600;color:#F7EDDC }
    .sc-lbl { margin-top:3px;font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.4) }
    .sc-right { position:relative;display:flex;align-items:center;justify-content:center }
    .sc-ring { position:absolute;border-radius:50%;border:1px solid rgba(216,199,164,.18) }
    .sc-r1 { width:min(420px,40vw);height:min(420px,40vw);animation:sc-spin 40s linear infinite }
    .sc-r2 { width:min(330px,31vw);height:min(330px,31vw);animation:sc-spinR 28s linear infinite }
    .sc-r3 { width:min(250px,24vw);height:min(250px,24vw);animation:sc-pulse 4s ease-in-out infinite }
    .sc-orbit { position:absolute;width:min(300px,29vw);height:min(300px,29vw);animation:sc-spin 18s linear infinite }
    .sc-orbit-dot { position:absolute;top:-4px;left:50%;transform:translateX(-50%);width:7px;height:7px;background:#D8C7A4;rotate:45deg;opacity:.65 }
    .sc-seal {
      position:relative;z-index:2;
      width:min(210px,20vw);height:min(210px,20vw);border-radius:50%;
      border:1px solid rgba(216,199,164,.42);
      background:radial-gradient(circle at 38% 34%,rgba(216,199,164,.12),transparent 60%);
      display:flex;align-items:center;justify-content:center;
      animation:sc-sealIn 1.2s cubic-bezier(.16,1,.3,1) .1s both;backdrop-filter:blur(4px);
    }
    .sc-logo { animation:sc-logoIn 1s ease .5s both;width:65%;height:65% }
    .sc-fcard {
      position:absolute;bottom:24px;right:0;width:min(310px,30vw);
      border-radius:20px;padding:20px;
      backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.18);
      background:rgba(255,255,255,.10);
      animation:sc-cardIn .8s cubic-bezier(.16,1,.3,1) 1.65s both;
    }
    .sc-fcard-top { display:flex;align-items:center;justify-content:space-between }
    .sc-fl { font-size:9px;letter-spacing:.24em;text-transform:uppercase;color:rgba(255,255,255,.42) }
    .sc-ft { margin-top:7px;font-family:'DM Serif Display',serif;font-size:16px;color:#F7EDDC }
    .sc-fbtn { width:38px;height:38px;flex-shrink:0;border-radius:50%;background:#9BA66B;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:700 }
    .sc-bar-bg { margin-top:16px;height:5px;border-radius:99px;background:rgba(255,255,255,.2);overflow:hidden }
    .sc-bar { height:100%;border-radius:99px;background:#D8C7A4;animation:sc-bar 1.4s ease 2s both }
    .sc-fdesc { margin-top:10px;font-size:11px;color:rgba(255,255,255,.48);line-height:1.6 }
  `;
  doc.head.appendChild(style);

  // Build the overlay HTML
  var overlay = doc.createElement('div');
  overlay.id = 'sc-intro-overlay';
  overlay.innerHTML = `
    <div class="sc-card">
      <div class="sc-bloom"></div>
      <div class="sc-dot" style="width:5px;height:5px;background:#D8C7A4;left:7%;top:20%;animation-delay:0s"></div>
      <div class="sc-dot" style="width:4px;height:4px;background:#9BA66B;left:16%;top:46%;animation-delay:.22s"></div>
      <div class="sc-dot" style="width:5px;height:5px;background:#D8C7A4;left:26%;top:16%;animation-delay:.4s"></div>
      <div class="sc-dot" style="width:4px;height:4px;background:#9BA66B;left:36%;top:73%;animation-delay:.58s"></div>
      <div class="sc-hline" style="left:10%;top:37%;width:78%;background:#D8C7A4;opacity:.15;animation-delay:.9s"></div>

      <div style="display:flex;flex-direction:column;justify-content:space-between;position:relative;z-index:2">
        <div>
          <div class="sc-badge"><span style="color:#9BA66B;font-size:14px">✦</span> Terra Magica intelligence</div>
          <p class="sc-eyebrow">Sales platform</p>
          <h1 class="sc-h1">San Canzian<br>Lead Generation</h1>
          <p class="sc-by">By Emma Lindemann</p>
        </div>
        <div class="sc-stats">
          <div class="sc-stat"><div class="sc-sym">✉</div><div class="sc-val">128</div><div class="sc-lbl">New enquiries</div></div>
          <div class="sc-stat"><div class="sc-sym">◆</div><div class="sc-val">46</div><div class="sc-lbl">Qualified leads</div></div>
          <div class="sc-stat"><div class="sc-sym">↗</div><div class="sc-val">18.4%</div><div class="sc-lbl">Conversion</div></div>
        </div>
      </div>

      <div class="sc-right">
        <div class="sc-ring sc-r1"></div>
        <div class="sc-ring sc-r2"></div>
        <div class="sc-ring sc-r3"></div>
        <div class="sc-orbit"><div class="sc-orbit-dot"></div></div>
        <div class="sc-seal">
          <svg class="sc-logo" viewBox="0 0 207.6 223.4" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 166.023,80.375 C 152.675,80.000 140.000,85.097 127.324,95.972 L 127.250,96.051 L 127.175,96.051 C 123.425,94.625 119.898,93.199 116.597,91.773 L 116.222,91.625 L 116.597,91.472 C 126.273,87.801 132.722,78.500 132.722,68.449 C 132.722,54.426 121.250,50.449 110.074,46.551 L 110.000,46.551 C 107.449,45.648 104.750,44.750 102.347,43.699 C 96.875,41.301 93.574,37.324 93.574,33.051 C 93.574,28.176 97.926,23.222 106.250,23.222 C 109.925,23.222 115.175,23.824 119.375,26.523 C 121.925,28.176 122.898,32.375 124.398,43.250 L 124.472,43.699 L 126.949,43.699 L 126.949,20.000 L 124.324,20.000 L 124.324,20.523 C 124.324,21.648 123.574,24.273 122.300,24.273 C 122.074,24.273 121.699,24.199 121.023,23.824 C 116.148,20.523 109.699,20.000 106.324,20.000 C 92.148,20.000 84.801,31.097 84.801,42.051 C 84.801,55.324 96.347,59.301 107.523,63.125 L 107.597,63.125 C 110.597,64.176 113.449,65.148 116.000,66.273 C 121.847,68.898 125.375,72.949 125.375,77.000 C 125.375,82.926 118.550,88.250 112.250,89.750 L 112.097,89.750 C 105.648,86.824 99.273,83.824 93.125,80.824 L 92.898,80.750 C 90.801,79.773 88.773,78.722 86.750,77.750 L 86.597,77.676 L 86.750,77.523 C 86.972,77.222 87.199,76.926 87.426,76.625 C 88.926,74.676 89.597,73.926 89.972,73.847 C 90.722,73.847 91.472,74.301 92.375,74.824 C 93.801,75.574 95.523,76.551 97.926,76.551 C 101.222,76.551 103.398,74.449 103.398,71.148 C 103.398,67.398 100.699,64.926 96.500,64.926 C 90.949,64.926 86.074,72.051 83.449,75.875 L 83.375,75.949 L 83.222,75.875 C 67.699,68.449 52.773,61.773 40.926,61.773 C 34.625,61.773 29.222,64.324 25.398,69.199 C 21.949,73.472 20.000,79.398 20.000,85.472 C 20.000,89.750 21.574,103.625 41.597,103.625 C 55.926,103.625 68.074,95.750 74.000,91.097 L 74.074,91.023 L 79.023,93.426 C 92.222,99.875 103.250,104.750 113.597,108.801 L 113.824,108.875 L 113.675,109.023 C 106.550,116.074 102.199,119.972 97.023,123.875 L 96.949,123.949 L 96.875,123.875 C 83.898,115.772 71.676,108.051 56.222,108.051 L 55.472,108.051 L 55.324,108.051 C 55.023,108.051 54.722,108.125 54.347,108.125 C 43.472,108.574 35.972,119.301 35.972,128.676 C 35.972,138.875 44.750,145.926 57.273,146.000 C 68.449,146.000 80.375,139.847 88.472,134.676 L 88.551,134.597 L 95.750,138.875 L 95.523,139.022 C 82.773,147.272 76.097,158.897 76.097,172.847 C 76.097,190.022 89.222,203.449 106.023,203.449 L 106.625,203.449 C 113.824,203.449 119.972,200.676 124.847,195.199 L 127.847,191.897 L 125.523,190.472 L 125.449,190.472 L 125.148,190.847 C 119.222,198.426 114.800,199.847 109.175,199.847 C 103.472,199.847 98.750,197.147 95.449,192.051 C 92.222,186.949 90.500,179.301 90.500,170.522 C 90.500,166.097 91.023,161.375 91.926,157.324 C 93.125,152.147 96.574,146.522 101.074,142.324 L 101.148,142.250 L 101.222,142.324 C 105.199,144.574 108.800,146.522 112.250,148.176 C 113.074,148.625 114.199,149.074 115.250,149.522 L 115.250,149.449 L 115.250,149.522 C 118.472,150.875 122.375,152.597 122.449,155.074 C 122.222,157.097 120.949,158.147 119.375,159.272 C 117.648,160.551 115.699,162.051 115.699,165.272 C 115.699,166.625 116.222,167.897 117.199,168.801 C 118.324,169.847 119.898,170.449 121.773,170.449 C 125.523,170.074 127.625,166.926 127.625,161.897 C 127.625,159.051 126.875,155.897 125.675,153.647 L 125.523,153.347 L 125.898,153.426 C 130.773,154.772 135.199,155.449 139.398,155.449 C 150.875,155.449 158.074,149.972 158.074,141.199 C 158.074,129.426 142.472,126.347 134.222,126.347 C 125.000,126.347 116.449,129.426 110.000,132.051 L 109.925,132.051 L 100.472,126.125 L 100.625,125.972 C 106.175,121.397 111.722,116.522 117.875,110.449 L 117.949,110.375 L 118.023,110.375 C 132.722,115.625 148.023,121.097 161.972,121.097 C 171.574,121.097 187.550,118.176 187.550,98.523 C 187.398,87.125 176.375,80.676 166.023,80.375 C 153.125,104.750 137.300,100.176 131.675,97.699 L 131.449,97.625 L 131.597,97.472 C 143.148,87.722 154.472,83.301 166.250,83.898 C 176.523,84.426 182.074,90.426 182.074,95.824 C 182.148,101.750 176.824,104.750 166.250,104.750 C 64.773,93.648 53.148,100.551 41.750,100.551 C 29.750,100.551 24.347,93.574 24.347,87.051 C 24.347,82.551 27.722,77.222 37.250,77.222 C 44.523,77.222 57.574,83.074 70.625,89.375 L 70.847,89.449 L 70.625,89.597 C 76.625,137.375 69.426,140.522 63.051,141.801 C 61.250,142.176 59.301,142.324 57.426,142.324 C 48.722,142.324 39.500,137.750 39.500,129.199 C 39.500,123.125 45.574,119.824 51.199,119.824 C 62.222,119.824 74.148,126.272 84.500,132.272 L 84.722,132.426 L 84.500,132.574 C 143.074,142.847 140.898,142.699 138.722,142.397 C 127.472,141.125 119.824,137.522 113.750,134.222 L 113.523,134.074 L 113.824,133.926 C 117.199,132.272 120.574,131.147 124.250,130.324 C 126.875,129.647 130.175,129.347 133.699,129.347 C 138.574,129.347 150.273,130.176 153.875,137.824 C 154.175,138.426 154.324,138.949 154.324,139.397 C 154.175,142.397 148.472,142.847 145.097,142.847" fill="#D8C7A4"/>
          </svg>
        </div>
        <div class="sc-fcard">
          <div class="sc-fcard-top">
            <div>
              <div class="sc-fl">Today's focus</div>
              <div class="sc-ft">DACH luxury operators</div>
            </div>
            <div class="sc-fbtn">›</div>
          </div>
          <div class="sc-bar-bg"><div class="sc-bar"></div></div>
          <div class="sc-fdesc">Lead quality rising from destination-led campaigns.</div>
        </div>
      </div>
    </div>
  `;
  doc.body.appendChild(overlay);

  // Auto-dismiss after 4.4s
  setTimeout(function() {
    overlay.classList.add('sc-out');
    setTimeout(function() { overlay.remove(); }, 950);
  }, 4400);
})();
</script>
"""
