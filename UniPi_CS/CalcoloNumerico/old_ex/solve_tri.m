function [x] = solve_tri(t,b)
    n=length(b);
    x(n)=b(n)/t(n,n);
    for k=n-1:-1:1
        s=0;
        for j=k+1:n
            s=s+t(k,j)+x(j);
        end
        x(k)=(b(k)-s)/t(k,k);
    end
end