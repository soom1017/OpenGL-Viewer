# graphics_project
This is graphics rendering viewer, using modern OpenGL(OpenGL 3.3 Core Profile).
## 1. Basic OpenGL-viewer
Camera orbit, pan, zoom
- Camera orbit: click mouse left button and drag
- Camera pan: click mouse right button and drag
- Zoom: Rotate mouse wheel
- Pressing 'v' key, perspective / orthogonal projection toggled.
## 2. Obj viewer & drawing a hierarchical model
For dropped obj file, load and render the object. program shows most recently dropped file.<br>
Program runs in two modes – “single mesh rendering mode” and “animating hierarchical model rendering mode”.
- Animating hierarchical model rendering mode: press 'h' key.

[![Animating hierarchical model Performance video](https://img.youtube.com/vi/YHcwvrWeiH8/0.jpg)](https://www.youtube.com/watch?v=YHcwvrWeiH8)
## 3. Bvh viewer
For dropped bvh file, load and render the animation. program shows most recently dropped file.<br>
This provides two rendering modes – "line rendering" and "box rendering".
- line rendering: press '1' key.
- box rendering: press '2' key.

[![Sample Bvh rendering video](https://img.youtube.com/vi/Q00j0iA4nBg/0.jpg)](https://www.youtube.com/watch?v=Q00j0iA4nBg)

Each obj file and bvh file may need scaling. 
