function [x] = solve_tri_up(t, b)
    n = length(b);
    x = zeros(n, 1);
    x(n) = b(n)/t(n, n);
    %%
    % 
    % $$e^{\pi i} + 1 = 0$$
    % 
    
    for k = n - 1 : -1 : 1
        s = 0;
        for j = k + 1 : n
            s = s + t(k, j) * x(j);
        end
        x(k) = (b(k) - s)/t(k, k);
    end
% matrice sparsa definizione
% gran parte matrici devono essere sparse sennò non stanno nemmeno in mem
% si riduce complessità nel for interno perché fa operazioni solo su
% elementi diversi da 0

% sparse(t) formato di memorizzazione matrice sparse (memorizza indici
% elementi diversi da 0 e il valore)
end