function [ ] = cerchio_2019(a, r, n) 
xx=linspace(0, 2*pi, n);
rex=real(a)+r*cos(xx);
imagx=imag(a)+r*sin(xx);
patch(rex, imagx, 'red');
axis equal;
end