(async function () {
  'use strict';
  const root = document.getElementById('fw3d');
  const canvas = root.querySelector('canvas');
  const status = document.getElementById('model-status');
  const loading = document.getElementById('loading');
  const $all = s => [...root.querySelectorAll(s)];
  function fail(message) {
    root.dataset.ready = 'error';
    loading.hidden = false;
    loading.classList.add('error');
    loading.querySelector('.spinner').hidden = true;
    document.getElementById('loading-title').textContent = 'Static preview';
    document.getElementById('loading-detail').textContent = message;
    status.textContent = 'Interactive view unavailable';
    $all('.controls').forEach(el => { el.disabled = true; });
  }
  try {
    if (!('DecompressionStream' in window)) throw Error('Open this file in a current Chrome, Edge, Firefox or Safari browser for the interactive model.');
    const bytes = Uint8Array.from(atob(document.getElementById('model-data').textContent.trim()), c => c.charCodeAt(0));
    const json = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
    const models = JSON.parse(json);
    const gl = canvas.getContext('webgl', {alpha:false, antialias:true});
    if (!gl) throw Error('3D graphics are unavailable in this browser. Open the file in a browser with WebGL enabled.');
    const shader = (type, source) => {
      const s = gl.createShader(type);
      gl.shaderSource(s,source); gl.compileShader(s);
      if (!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw Error('The 3D renderer could not start. Try another browser.');
      return s;
    };
    const program = gl.createProgram();
    gl.attachShader(program,shader(gl.VERTEX_SHADER,`attribute vec3 aPosition;attribute vec3 aNormal;uniform mat4 uMVP;uniform vec3 uOrigin;varying vec3 vNormal;void main(){vNormal=aNormal;gl_Position=uMVP*vec4(aPosition*.01+uOrigin,1.0);}`));
    gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`precision mediump float;uniform vec3 uColor;uniform vec3 uLight;varying vec3 vNormal;void main(){vec3 n=normalize(vNormal);if(!gl_FrontFacing)n=-n;float diffuse=max(dot(n,uLight),0.0);float sky=max(n.z,0.0);float lighting=.42+.48*diffuse+.1*sky;float spec=.06*pow(diffuse,20.0);gl_FragColor=vec4(uColor*lighting+spec,1.0);}`));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program,gl.LINK_STATUS)) throw Error('The 3D renderer could not start. Try another browser.');
    gl.useProgram(program);
    const loc = {position:gl.getAttribLocation(program,'aPosition'),normal:gl.getAttribLocation(program,'aNormal'),mvp:gl.getUniformLocation(program,'uMVP'),origin:gl.getUniformLocation(program,'uOrigin'),color:gl.getUniformLocation(program,'uColor'),light:gl.getUniformLocation(program,'uLight')};
    gl.enableVertexAttribArray(loc.position); gl.enableVertexAttribArray(loc.normal); gl.enable(gl.DEPTH_TEST);
    const decode = (s,Type) => new Type(Uint8Array.from(atob(s),c=>c.charCodeAt(0)).buffer);
    const buffer = (target,data) => { const b=gl.createBuffer();gl.bindBuffer(target,b);gl.bufferData(target,data,gl.STATIC_DRAW);return b; };
    const palette = {print:[.32,.53,.50],metal:[.65,.73,.74],buy:[.45,.55,.57],electronics:[.31,.56,.45]};
    const colors = {P01:[.57,.70,.66],P04:[.83,.59,.33],P05:[.37,.54,.52],P06L:[.31,.48,.46],P06R:[.31,.48,.46],P08:[.36,.58,.49],P09:[.32,.50,.43]};
    const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
    models.forEach(m => {
      const points=decode(m.v,Int16Array);
      for(let i=0;i<points.length;i+=3) for(let k=0;k<3;k++) { const v=points[i+k]*.01+m.origin[k];min[k]=Math.min(min[k],v);max[k]=Math.max(max[k],v); }
      m.vertices=buffer(gl.ARRAY_BUFFER,points);m.normals=buffer(gl.ARRAY_BUFFER,decode(m.n,Int8Array));m.indices=buffer(gl.ELEMENT_ARRAY_BUFFER,decode(m.f,Uint16Array));m.color=colors[m.id]||palette[m.group];
      delete m.v;delete m.n;delete m.f;
    });
    const v3={sub:(a,b)=>a.map((v,i)=>v-b[i]),dot:(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],unit:a=>{const l=Math.hypot(...a);return a.map(v=>v/l);}};
    const multiply=(a,b)=>{const out=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)out[c*4+r]+=a[k*4+r]*b[c*4+k];return out;};
    const perspective=(fov,aspect,near,far)=>{const f=1/Math.tan(fov/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]);};
    const basis=()=>{const ce=Math.cos(camera.elevation);const z=[ce*Math.cos(camera.yaw),ce*Math.sin(camera.yaw),Math.sin(camera.elevation)],x=v3.unit(v3.cross([0,0,1],z)),y=v3.cross(z,x);return {x,y,z};};
    const viewMatrix=(eye,b)=>new Float32Array([b.x[0],b.y[0],b.z[0],0,b.x[1],b.y[1],b.z[1],0,b.x[2],b.y[2],b.z[2],0,-v3.dot(b.x,eye),-v3.dot(b.y,eye),-v3.dot(b.z,eye),1]);
    const center=min.map((v,i)=>(v+max[i])/2);
    const corners=[];
    for(let i=0;i<8;i++)corners.push([i&1?max[0]:min[0],i&2?max[1]:min[1],i&4?max[2]:min[2]]);
    let mode='all',pending=false,first=true,fitOnResize=true;
    const camera={yaw:-2.42,elevation:.70,distance:310,target:[...center]};
    function fit(){
      const b=basis(),rect=canvas.getBoundingClientRect(),aspect=rect.width/Math.max(rect.height,1),tan=Math.tan(.69/2);
      camera.target=[...center]; let distance=100;
      corners.forEach(p=>{const d=v3.sub(p,center);distance=Math.max(distance,Math.abs(v3.dot(d,b.x))*1.20/(tan*aspect)+v3.dot(d,b.z),Math.abs(v3.dot(d,b.y))*1.26/tan+v3.dot(d,b.z));});
      camera.distance=distance;
    }
    function shown(m){
      if(mode==='mechanics')return m.group!=='electronics'&&!['P08','P09'].includes(m.id);
      if(mode==='inside')return !['P01','P09'].includes(m.id);
      if(mode==='plastic')return m.group==='print';
      return true;
    }
    const descriptions={all:'Complete assembly',mechanics:'Mechanism · PCB and enclosure hidden',inside:'Inside view · frame and lid hidden',plastic:'8 printed components'};
    function sync(){
      $all('[data-mode]').forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.mode===mode)));
      status.textContent=descriptions[mode];
      root.dataset.mode=mode;
      root.dataset.visibleParts=String(models.filter(shown).length);
      request();
    }
    function request(){if(!pending){pending=true;requestAnimationFrame(render);}}
    function render(){
      pending=false;
      const rect=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));
      if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
      gl.viewport(0,0,w,h);gl.clearColor(.929,.945,.933,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      const b=basis(),eye=camera.target.map((v,i)=>v+camera.distance*b.z[i]);
      const mvp=multiply(perspective(.69,w/h,1,2500),viewMatrix(eye,b));
      gl.uniformMatrix4fv(loc.mvp,false,mvp);gl.uniform3fv(loc.light,v3.unit(b.z.map((v,i)=>v+[0,0,.35][i])));
      models.filter(shown).forEach(m=>{
        gl.bindBuffer(gl.ARRAY_BUFFER,m.vertices);gl.vertexAttribPointer(loc.position,3,gl.SHORT,false,0,0);
        gl.bindBuffer(gl.ARRAY_BUFFER,m.normals);gl.vertexAttribPointer(loc.normal,3,gl.BYTE,true,0,0);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,m.indices);gl.uniform3fv(loc.origin,m.origin);gl.uniform3fv(loc.color,m.color);gl.drawElements(gl.TRIANGLES,m.count,gl.UNSIGNED_SHORT,0);
      });
      if(first){first=false;loading.hidden=true;root.dataset.ready='true';$all('.controls').forEach(el=>{el.disabled=false;});}
    }
    function orient(view){
      const presets={iso:[-2.42,.70],top:[-Math.PI/2,1.54],side:[-Math.PI/2,.02],bottom:[-Math.PI/2,-1.54]};
      [camera.yaw,camera.elevation]=presets[view];fitOnResize=true;fit();request();
    }
    function zoom(factor){fitOnResize=false;camera.distance=Math.max(70,Math.min(1400,camera.distance*factor));request();}
    function pan(dx,dy){const b=basis(),scale=2*camera.distance*Math.tan(.69/2)/Math.max(canvas.clientHeight,1);camera.target=camera.target.map((v,i)=>v+(-b.x[i]*dx+b.y[i]*dy)*scale);}
    $all('[data-mode]').forEach(el=>el.addEventListener('click',()=>{mode=el.dataset.mode;sync();}));
    $all('[data-view]').forEach(el=>el.addEventListener('click',()=>orient(el.dataset.view)));
    $all('[data-action]').forEach(el=>el.addEventListener('click',()=>{if(el.dataset.action==='reset'){mode='all';orient('iso');sync();}else zoom(el.dataset.action==='zoom-in'?.82:1/.82);}));
    const pointers=new Map();
    const pair=()=>{const p=[...pointers.values()];return {x:(p[0].x+p[1].x)/2,y:(p[0].y+p[1].y)/2,d:Math.hypot(p[1].x-p[0].x,p[1].y-p[0].y)};};
    canvas.addEventListener('pointerdown',e=>{canvas.focus({preventScroll:true});canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});canvas.classList.add('dragging');});
    canvas.addEventListener('pointermove',e=>{
      if(!pointers.has(e.pointerId))return;
      fitOnResize=false;
      const old=pointers.get(e.pointerId),before=pointers.size>=2?pair():null;
      pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
      if(before){const after=pair();if(before.d>3&&after.d>3)zoom(before.d/after.d);pan(after.x-before.x,after.y-before.y);}
      else{const dx=e.clientX-old.x,dy=e.clientY-old.y;if(e.shiftKey||e.buttons===2)pan(dx,dy);else{camera.yaw-=dx*.008;camera.elevation=Math.max(-1.54,Math.min(1.54,camera.elevation+dy*.008));}}
      request();
    });
    function end(e){pointers.delete(e.pointerId);if(!pointers.size)canvas.classList.remove('dragging');}
    ['pointerup','pointercancel','lostpointercapture'].forEach(type=>canvas.addEventListener(type,end));
    canvas.addEventListener('contextmenu',e=>e.preventDefault());
    canvas.addEventListener('wheel',e=>{e.preventDefault();zoom(Math.exp(Math.max(-200,Math.min(200,e.deltaY))*.0015));},{passive:false});
    canvas.addEventListener('keydown',e=>{
      let handled=true;
      if(e.key==='ArrowLeft')camera.yaw+=.12;else if(e.key==='ArrowRight')camera.yaw-=.12;
      else if(e.key==='ArrowUp')camera.elevation=Math.min(1.54,camera.elevation+.12);else if(e.key==='ArrowDown')camera.elevation=Math.max(-1.54,camera.elevation-.12);
      else if(e.key==='+'||e.key==='=')zoom(.9);else if(e.key==='-')zoom(1/.9);else if(e.key==='Home')orient('iso');else handled=false;
      if(handled){e.preventDefault();request();}
    });
    canvas.addEventListener('dblclick',()=>orient('iso'));
    canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail('The 3D graphics session was interrupted. Reopen the file to restore the interactive view.');});
    new ResizeObserver(()=>{if(fitOnResize)fit();request();}).observe(canvas);
    fit();sync();
  }catch(error){fail(error.message||'The interactive model could not be opened. Try another browser.');}
})();
