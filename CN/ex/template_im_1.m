function [a,iter] = template_im_1(b,tol,maxiter)
if (norm(b-b2, inf)>0)
    disp('matrice non simmetrica');
    return
end
for iter=1:maxiter
    a=(b+inv(b))/2;
    err=norm(a-b, inf)/norm(a, inf)
    if(err<=tol)
        disp('convergenza entro il numero di iterazioni');
        break
    end
    b=a;
end
end
