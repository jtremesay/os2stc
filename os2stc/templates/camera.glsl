mat3 set_camera( in vec3 origin, in vec3 target, float roll)
{
	vec3 cw = normalize(target - origin);
	vec3 cp = vec3(sin(roll), cos(roll), 0.0);
	vec3 cu = normalize(cross(cw, cp));
	vec3 cv = (cross(cu, cw));
    return mat3(cu, cv, cw);
}