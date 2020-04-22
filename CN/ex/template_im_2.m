function [a,iter] = template_im_2(b,tol,maxiter)
if (norm(b-b2, inf)>0)
    disp('matrice non simmetrica');
    return
end
%criterio: fermati quando err<=tol o iter>maxiter
%quind: lavora quando err>tol e iter<=maxiter
err=inf;
iter=0;
while(err>tol & iter<=maxiter)
    a=(b+inv(b))/2;
    err=norm(a-b, inf)/norm(a,inf);
    b=a;
    iter=iter+1;
end
end
