// Rigged cartoon characters (SVG). Both face right; local origin = ground point under the body.
const INK = "#121a38", SW = 5;
const st = `stroke="${INK}" stroke-width="${SW}" stroke-linejoin="round" stroke-linecap="round"`;

window.HARE_SVG = `
<g id="hare">
  <ellipse id="hShadow" cx="0" cy="4" rx="150" ry="14" fill="#000" opacity=".38" filter="url(#soft)"/>
  <g id="hHop">
   <g id="hBody">
    <!-- far legs (darker) -->
    <g id="hHindFar">
      <path d="M -150 -100 C -152 -150 -70 -160 -48 -112 C -34 -76 -64 -40 -104 -40 C -136 -40 -150 -66 -150 -100 Z" fill="#b9c6de" ${st}/>
      <path d="M -150 -34 C -152 -12 -70 -4 -44 -10 C -30 -14 -34 -30 -48 -34 C -84 -42 -140 -48 -150 -34 Z" fill="#b9c6de" ${st}/>
    </g>
    <g id="hFrontFar"><path d="M 60 -100 C 54 -62 58 -26 62 -10 C 64 0 94 2 96 -10 C 98 -24 92 -64 90 -100 Z" fill="#b9c6de" ${st}/></g>
    <!-- tail -->
    <path id="hTail" d="M -150 -150 C -190 -175 -206 -120 -178 -110 C -196 -92 -160 -70 -146 -96 Z" fill="#ffffff" ${st}/>
    <!-- torso -->
    <path d="M -156 -112 C -166 -196 -44 -238 40 -208 C 114 -182 136 -124 114 -84 C 94 -46 22 -40 -40 -46 C -112 -52 -150 -72 -156 -112 Z" fill="#f5f7fc" ${st}/>
    <path d="M -140 -86 C -110 -58 -40 -52 20 -54 C 70 -56 100 -68 112 -90 C 100 -52 30 -42 -40 -48 C -100 -52 -134 -64 -140 -86 Z" fill="#c9d4ea"/>
    <path d="M -100 -190 C -60 -214 10 -216 50 -196" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity=".9"/>
    <!-- near legs -->
    <g id="hHind">
      <path d="M -160 -104 C -162 -156 -76 -168 -50 -118 C -36 -80 -64 -40 -108 -38 C -142 -38 -158 -66 -160 -104 Z" fill="#f5f7fc" ${st}/>
      <path d="M -120 -150 C -150 -140 -156 -100 -140 -78" fill="none" stroke="#c9d4ea" stroke-width="10" stroke-linecap="round"/>
      <g id="hHindFoot"><path d="M -164 -30 C -166 -6 -80 2 -50 -6 C -34 -10 -38 -28 -54 -32 C -90 -40 -152 -46 -164 -30 Z" fill="#f5f7fc" ${st}/></g>
    </g>
    <g id="hFront"><path d="M 74 -100 C 68 -62 72 -26 76 -10 C 78 0 110 2 112 -10 C 114 -24 108 -64 104 -100 Z" fill="#f5f7fc" ${st}/>
      <path d="M 82 -8 L 84 -2 M 94 -8 L 95 -1" ${st} stroke-width="3"/></g>
    <!-- head -->
    <g id="hHead">
      <g id="hEarB"><path d="M 118 -250 C 88 -310 84 -410 110 -452 C 138 -410 146 -316 140 -252 Z" fill="#dfe6f4" ${st}/></g>
      <g id="hEarF"><path d="M 146 -254 C 124 -318 128 -420 158 -462 C 184 -414 184 -318 168 -254 Z" fill="#f5f7fc" ${st}/>
        <path d="M 150 -270 C 138 -320 142 -400 158 -436 C 172 -398 172 -322 162 -272 Z" fill="#f4a9bd"/></g>
      <path d="M 62 -196 C 50 -258 112 -300 168 -280 C 220 -262 238 -208 212 -170 C 192 -142 146 -134 108 -144 C 78 -152 66 -170 62 -196 Z" fill="#f5f7fc" ${st}/>
      <path d="M 80 -160 C 110 -140 160 -138 200 -160 C 180 -140 130 -134 100 -146 Z" fill="#c9d4ea"/>
      <ellipse cx="192" cy="-176" rx="18" ry="10" fill="#f7a9bf" opacity=".55"/>
      <g id="hEye">
        <ellipse cx="170" cy="-222" rx="21" ry="26" fill="#ffffff" ${st} stroke-width="4"/>
        <g id="hPupil"><circle cx="176" cy="-218" r="11" fill="${INK}"/><circle cx="180" cy="-223" r="4" fill="#fff"/></g>
        <clipPath id="hEyeClip"><ellipse cx="170" cy="-222" rx="21" ry="26"/></clipPath>
        <g clip-path="url(#hEyeClip)"><g id="hLid"><rect x="140" y="-300" width="62" height="78" fill="#e9eef8"/>
          <path d="M 144 -222 C 158 -228 182 -228 196 -222" fill="none" ${st} stroke-width="4"/></g></g>
        <ellipse cx="170" cy="-222" rx="21" ry="26" fill="none" ${st} stroke-width="4"/>
      </g>
      <path id="hBrow" d="M 150 -262 C 162 -272 182 -272 194 -262" fill="none" ${st} stroke-width="6"/>
      <path d="M 214 -196 C 226 -198 230 -186 222 -180 C 214 -176 206 -186 214 -196 Z" fill="#e57a95" ${st} stroke-width="3"/>
      <path id="hMouth" d="M 198 -170 C 206 -160 220 -162 228 -174" fill="none" ${st} stroke-width="4"/>
      <path d="M 222 -186 L 262 -196 M 222 -180 L 262 -178 M 220 -174 L 256 -160" stroke="${INK}" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>
    </g>
   </g>
  </g>
</g>`;

window.TORT_SVG = `
<g id="tort">
  <ellipse cx="0" cy="4" rx="175" ry="14" fill="#000" opacity=".38" filter="url(#soft)"/>
  <g id="tBody">
    <g id="tLegBF"><path d="M -112 -44 C -118 -14 -114 4 -98 10 C -82 16 -62 12 -58 0 C -54 -14 -62 -34 -66 -44 Z" fill="#6f86b0" ${st}/></g>
    <g id="tLegFF"><path d="M 58 -44 C 52 -14 56 4 72 10 C 88 16 108 12 112 0 C 116 -14 108 -34 104 -44 Z" fill="#6f86b0" ${st}/></g>
    <path d="M -160 -52 L -198 -36 L -156 -30 Z" fill="#9fb3d6" ${st}/>
    <g id="tHead">
      <path d="M 110 -70 C 140 -92 166 -98 186 -94 L 196 -60 C 172 -54 140 -50 116 -48 Z" fill="#9fb3d6" ${st}/>
      <path d="M 160 -110 C 176 -156 258 -156 270 -110 C 280 -72 240 -52 204 -56 C 172 -60 152 -80 160 -110 Z" fill="#a9bddf" ${st}/>
      <path d="M 170 -80 C 196 -64 240 -62 262 -84 C 250 -60 214 -54 190 -60 Z" fill="#8aa0c9"/>
      <g id="tEye">
        <ellipse cx="232" cy="-116" rx="17" ry="20" fill="#fff" ${st} stroke-width="4"/>
        <g id="tPupil"><circle cx="238" cy="-112" r="9" fill="${INK}"/><circle cx="241" cy="-116" r="3" fill="#fff"/></g>
        <clipPath id="tEyeClip"><ellipse cx="232" cy="-116" rx="17" ry="20"/></clipPath>
        <g clip-path="url(#tEyeClip)"><g id="tLid"><rect x="206" y="-180" width="52" height="64" fill="#a9bddf"/>
          <path d="M 210 -116 C 224 -121 242 -121 254 -115" fill="none" ${st} stroke-width="4"/></g></g>
        <ellipse cx="232" cy="-116" rx="17" ry="20" fill="none" ${st} stroke-width="4"/>
      </g>
      <path id="tBrow" d="M 214 -144 C 226 -146 240 -142 252 -134" fill="none" ${st} stroke-width="6"/>
      <path d="M 250 -82 C 258 -76 266 -78 270 -86" fill="none" ${st} stroke-width="4"/>
      <ellipse cx="226" cy="-86" rx="12" ry="7" fill="#f2a6bb" opacity=".5"/>
    </g>
    <path d="M -156 -48 C -146 -156 -56 -214 8 -214 C 92 -214 152 -150 158 -48 Z" fill="url(#shell)" ${st}/>
    <clipPath id="tShellClip"><path d="M -156 -48 C -146 -156 -56 -214 8 -214 C 92 -214 152 -150 158 -48 Z"/></clipPath>
    <g clip-path="url(#tShellClip)" fill="#3c6fc8" stroke="#9fd0ff" stroke-width="5" stroke-linejoin="round">
      <path d="M 50 -130 L 26 -88 L -22 -88 L -46 -130 L -22 -172 L 26 -172 Z"/>
      <path d="M -54 -88 L -76 -50 L -120 -50 L -142 -88 L -120 -126 L -76 -126 Z"/>
      <path d="M 142 -88 L 120 -50 L 76 -50 L 54 -88 L 76 -126 L 120 -126 Z"/>
      <path d="M -60 -174 L -80 -140 L -118 -140 L -130 -170 L -110 -206 L -72 -206 Z"/>
      <path d="M 124 -174 L 104 -140 L 66 -140 L 54 -170 L 74 -206 L 112 -206 Z"/>
      <path d="M -170 -48 C -120 -120 -40 -150 60 -150 C 120 -150 160 -110 180 -48 Z" fill="#000" stroke="none" opacity=".12" transform="translate(40 34)"/>
    </g>
    <path d="M -96 -176 C -60 -202 -10 -206 30 -196" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" opacity=".35"/>
    <path d="M -172 -50 C -60 -28 80 -28 176 -50 C 182 -32 166 -20 144 -18 C 60 -10 -60 -10 -144 -18 C -166 -20 -178 -32 -172 -50 Z" fill="#1c3f82" ${st}/>
    <g id="tLegBN"><path d="M -88 -30 C -94 0 -90 18 -72 24 C -54 30 -32 26 -28 12 C -24 -2 -32 -22 -36 -30 Z" fill="#a9bddf" ${st}/></g>
    <g id="tLegFN"><path d="M 84 -30 C 78 0 82 18 100 24 C 118 30 140 26 144 12 C 148 -2 140 -22 136 -30 Z" fill="#a9bddf" ${st}/></g>
  </g>
</g>`;
