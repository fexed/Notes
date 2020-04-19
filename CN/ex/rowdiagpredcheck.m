function [isPredominanteDiagonalePerRighe] = rowdiagpredcheck(matrix)
%ROWDIAGPREDCHECK Controlla se matrix è predominante diagonale per righe
isPredominanteDiagonalePerRighe = 1;
[n, m] = size(matrix); % numero di righe e colonne della matrice
for i = 1:n
   aii = abs(matrix(i, i)); % |matrix(i, i)|
   sum = 0;
   for j = 1:m % somma degli altri elementi sulla riga
       if (i ~= j)
           sum = sum + abs(matrix(i, j));
       end
   end
   % check |matrix(i,i)| > sum(j=1:m, j!=i)(|matrix(i,j)|)
   if (aii <= sum)
       isPredominanteDiagonalePerRighe = 0;
       break;
   end
end
end