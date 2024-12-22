// Generated by os2stc - OpenSCAD to Shadertoy converter
//
// Use code from https://www.shadertoy.com/view/Xds3zN which is licensed under following terms:
// The MIT License
// Copyright © 2013 Inigo Quilez
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

#if HW_PERFORMANCE==0
#define AA 1
#else
#define AA 2   // make this 2 or 3 for antialiasing
#endif

{% include "maths.glsl" %}
{% include "sdf.glsl" %}

vec2 map( in vec3 pos )
{
    vec2 res = vec2( pos.y, 0.0 );

    {{ ast }}


    return res;
}

{% include "render.glsl" %}
{% include "camera.glsl" %}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 mouse = iMouse.xy / iResolution.xy;
	float time = 32.0 + iTime * 1.5;

    // camera	
    vec3 camera_target = vec3(0.0, 0.0, 0.0);
    float camera_radius = 4.5;
    float camera_speed = 0.1;
    vec3 camera_origin = camera_target + vec3(
        camera_radius * cos(camera_speed * time + 7.0 * mouse.x), 
        2.2, 
        camera_radius*sin(camera_speed * time + 7.0 * mouse.x)
    );
    
    // camera-to-world transformation
    mat3 camera = set_camera(camera_origin, camera_target, 0.0);

    vec3 tot = vec3(0.0);
#if AA>1
    for (int m = 0; m < AA; m++ ) {
        for( int n = 0; n < AA; n++ ) {
            // pixel coordinates
            vec2 o = vec2(float(m), float(n)) / float(AA) - 0.5;
            vec2 p = (2.0 * (fragCoord + o)-iResolution.xy) / iResolution.y;
#else    
            vec2 p = (2.0 * fragCoord - iResolution.xy) / iResolution.y;
#endif

            // focal length
            const float focal_length = 2.5;
            
            // ray direction
            vec3 ray_direction = camera * normalize(vec3(p, focal_length));

            // ray differentials
            vec2 px = (2.0 * (fragCoord + vec2(1.0, 0.0)) - iResolution.xy) / iResolution.y;
            vec2 py = (2.0 * (fragCoord + vec2(0.0, 1.0)) - iResolution.xy) / iResolution.y;
            vec3 rdx = camera * normalize(vec3(px, focal_length));
            vec3 rdy = camera * normalize(vec3(py, focal_length));
            
            // render	
            vec3 col = render(camera_origin, ray_direction, rdx, rdy);

            // gain
            // col = col*3.0/(2.5+col);
            
            // gamma
            col = pow(col, vec3(0.4545));

            tot += col;
#if AA>1
        }
    }

    tot /= float(AA * AA);
#endif
    
    fragColor = vec4(tot, 1.0);
}