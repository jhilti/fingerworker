(async function(){
  'use strict';
  const root=document.getElementById('fw3d'), canvas=root.querySelector('canvas'), note=root.querySelector('.fw3d-status');
  const $=s=>root.querySelector(s), $$=s=>[...root.querySelectorAll(s)];
  try {
    const bytes=Uint8Array.from(atob(root.querySelector('.fw3d-data').textContent.trim()),c=>c.charCodeAt(0));
    const json=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
    const models=JSON.parse(json);
    const gl=canvas.getContext('webgl',{alpha:false,antialias:true,preserveDrawingBuffer:true});
    if(!gl)throw Error('WebGL ist in diesem Browser nicht verfügbar. Die Download-Dateien funktionieren unabhängig von dieser Ansicht.');
    const shader=(type,src)=>{const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(sh));return sh;};
    const program=gl.createProgram();
    gl.attachShader(program,shader(gl.VERTEX_SHADER,`attribute vec3 aPosition;attribute vec3 aNormal;uniform mat4 uMVP;uniform vec3 uOrigin;varying vec3 vNormal;void main(){vNormal=aNormal;gl_Position=uMVP*vec4(aPosition*.01+uOrigin,1.0);}`));
    gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`precision mediump float;uniform vec4 uColor;uniform vec3 uLight;varying vec3 vNormal;void main(){vec3 n=normalize(vNormal);if(!gl_FrontFacing)n=-n;float light=.48+.52*max(dot(n,uLight),0.0);float rim=.09*pow(1.0-abs(n.z),3.0);gl_FragColor=vec4(uColor.rgb*light+rim,uColor.a);}`));
    gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
    const loc={pos:gl.getAttribLocation(program,'aPosition'),normal:gl.getAttribLocation(program,'aNormal'),mvp:gl.getUniformLocation(program,'uMVP'),origin:gl.getUniformLocation(program,'uOrigin'),color:gl.getUniformLocation(program,'uColor'),light:gl.getUniformLocation(program,'uLight')};
    gl.enableVertexAttribArray(loc.pos);gl.enableVertexAttribArray(loc.normal);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    const decode=(str,Type)=>{const buf=Uint8Array.from(atob(str),c=>c.charCodeAt(0)).buffer;return new Type(buf);};
    const buffer=(target,data)=>{const b=gl.createBuffer();gl.bindBuffer(target,b);gl.bufferData(target,data,gl.STATIC_DRAW);return b;};
    const palette={print:[.19,.51,.65],metal:[.50,.56,.65],buy:[.81,.51,.21],electronics:[.24,.65,.48]};
    const custom={P01:[.70,.77,.81],P04:[.18,.53,.72],P05:[.20,.40,.55],P08:[.22,.63,.53],P09:[.18,.48,.42],P06L:[.40,.54,.68],P06R:[.40,.54,.68]};
    models.forEach(m=>{m.positions=decode(m.v,Int16Array);m.vertices=buffer(gl.ARRAY_BUFFER,m.positions);m.normals=buffer(gl.ARRAY_BUFFER,decode(m.n,Int8Array));m.indices=buffer(gl.ELEMENT_ARRAY_BUFFER,decode(m.f,Uint16Array));m.color=custom[m.id]||palette[m.group];delete m.v;delete m.n;delete m.f;});
    const v3={sub:(a,b)=>a.map((x,i)=>x-b[i]),dot:(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0),cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],unit:a=>{let l=Math.hypot(...a);return a.map(x=>x/l);}};
    const multiply=(a,b)=>{let o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o;};
    const perspective=(fov,aspect,near,far)=>{const f=1/Math.tan(fov/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]);};
    const lookAt=(eye,target)=>{const z=v3.unit(v3.sub(eye,target)),x=v3.unit(v3.cross([0,0,1],z)),y=v3.cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-v3.dot(x,eye),-v3.dot(y,eye),-v3.dot(z,eye),1]);};
    const defaults={yaw:-2.42,elevation:.70,distance:310,target:[40.5,-1,12]};
    let camera,visible={print:true,metal:true,buy:true,electronics:true},frame='solid',lid=true,pending=false,mvp;
    function resetCamera(){camera={...defaults,target:[...defaults.target]};}
    resetCamera();
    const requested=()=>{if(!pending){pending=true;requestAnimationFrame(render);}};
    function shown(m){return visible[m.group]&&(m.id!=='P01'||frame!=='hidden')&&(m.id!=='P09'||lid);}
    function draw(m,alpha){gl.bindBuffer(gl.ARRAY_BUFFER,m.vertices);gl.vertexAttribPointer(loc.pos,3,gl.SHORT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,m.normals);gl.vertexAttribPointer(loc.normal,3,gl.BYTE,true,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,m.indices);gl.uniform3fv(loc.origin,m.origin);gl.uniform4fv(loc.color,[...m.color,alpha]);gl.drawElements(gl.TRIANGLES,m.count,gl.UNSIGNED_SHORT,0);}
    function render(){
      pending=false;const rect=canvas.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.viewport(0,0,w,h);gl.clearColor(.961,.973,.973,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      const ce=Math.cos(camera.elevation),eye=[camera.target[0]+camera.distance*ce*Math.cos(camera.yaw),camera.target[1]+camera.distance*ce*Math.sin(camera.yaw),camera.target[2]+camera.distance*Math.sin(camera.elevation)];
      mvp=multiply(perspective(.69,w/h,1,1800),lookAt(eye,camera.target));gl.uniformMatrix4fv(loc.mvp,false,mvp);gl.uniform3fv(loc.light,v3.unit(v3.sub(eye,camera.target)));
      gl.depthMask(true);let count=0;models.filter(shown).forEach(m=>{count++;if(m.id!=='P01'||frame!=='transparent')draw(m,1);});
      if(visible.print&&frame==='transparent'){gl.depthMask(false);draw(models.find(m=>m.id==='P01'),.16);gl.depthMask(true);}
      note.textContent=count+' von '+models.length+' CAD-Körpern sichtbar · R20';
    }
    function sync(){ $$('input[data-group]').forEach(el=>el.checked=visible[el.dataset.group]);$('[data-frame]').value=frame;$('[data-lid]').checked=lid;requested();}
    $$('input[data-group]').forEach(el=>el.addEventListener('change',()=>{visible[el.dataset.group]=el.checked;requested();}));
    $('[data-frame]').addEventListener('change',e=>{frame=e.target.value;requested();});
    $('[data-lid]').addEventListener('change',e=>{lid=e.target.checked;requested();});
    $$('button[data-view]').forEach(el=>el.addEventListener('click',()=>{const action=el.dataset.view;if(action==='all'){visible={print:true,metal:true,buy:true,electronics:true};frame='solid';lid=true;}if(action==='print'){visible={print:true,metal:false,buy:false,electronics:false};frame='solid';lid=true;}if(action==='inside'){visible={print:true,metal:true,buy:true,electronics:true};frame='transparent';lid=false;}if(action==='reset'){resetCamera();visible={print:true,metal:true,buy:true,electronics:true};frame='solid';lid=true;}if(action==='top'){camera.yaw=-Math.PI/2;camera.elevation=1.54;}if(action==='bottom'){camera.yaw=-Math.PI/2;camera.elevation=-1.15;}sync();}));
    let last=null,dragged=false;
    canvas.addEventListener('pointerdown',e=>{canvas.focus({preventScroll:true});canvas.setPointerCapture(e.pointerId);last={x:e.clientX,y:e.clientY};dragged=false;canvas.classList.add('fw3d-dragging');});
    canvas.addEventListener('pointermove',e=>{if(!last)return;const dx=e.clientX-last.x,dy=e.clientY-last.y;dragged=dragged||Math.abs(dx)+Math.abs(dy)>3;last={x:e.clientX,y:e.clientY};if(e.shiftKey||e.buttons===2){const scale=camera.distance*.0014;camera.target[0]+=(-Math.sin(camera.yaw)*dx+Math.cos(camera.yaw)*dy)*scale;camera.target[1]+=(Math.cos(camera.yaw)*dx+Math.sin(camera.yaw)*dy)*scale;}else{camera.yaw-=dx*.008;camera.elevation=Math.max(-1.54,Math.min(1.54,camera.elevation+dy*.008));}requested();});
    function end(){last=null;canvas.classList.remove('fw3d-dragging');}canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);
    canvas.addEventListener('contextmenu',e=>e.preventDefault());
    canvas.addEventListener('wheel',e=>{e.preventDefault();camera.distance=Math.max(75,Math.min(900,camera.distance*Math.exp(e.deltaY*.001)));requested();},{passive:false});
    canvas.addEventListener('keydown',e=>{let handled=true;if(e.key==='ArrowLeft')camera.yaw+=.12;else if(e.key==='ArrowRight')camera.yaw-=.12;else if(e.key==='ArrowUp')camera.elevation=Math.min(1.54,camera.elevation+.12);else if(e.key==='ArrowDown')camera.elevation=Math.max(-1.54,camera.elevation-.12);else if(e.key==='+'||e.key==='=')camera.distance=Math.max(75,camera.distance*.9);else if(e.key==='-')camera.distance=Math.min(900,camera.distance/ .9);else if(e.key==='Home')resetCamera();else handled=false;if(handled){e.preventDefault();requested();}});
    canvas.addEventListener('dblclick',()=>{resetCamera();requested();});
    new ResizeObserver(requested).observe(canvas);window.addEventListener('resize',requested);requested();
    root.dataset.ready='true';
  }catch(error){note.textContent=error.message;root.dataset.ready='error';console.error('Fingerworker 3D:',error);}
})();
