function [] = circle_gershgorin(a)
    %A Matrice nxn
    n=length(a);
    for k=1:n
        r=0;
        for j=1:k-1
            r=r+abs(a(k,j));
        end
        for j=k+1:n
            r=r+abs(a(k,j));
        end
        circle(a(k,k), r);
    end
end

