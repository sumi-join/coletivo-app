-- Nanda (Fernanda Keller Garcia), líder de operações — os dois e-mails que ela passou no grupo em 08/06/2026.
-- Para incluir outra pessoa: mesma linha com o e-mail Google dela (minúsculo). Para tirar: update equipe set ativo=false where email='...';
insert into public.equipe (email, nome, papel) values
  ('fernandakgarcia@gmail.com', 'Nanda (Fernanda Keller Garcia)', 'operação'),
  ('fernanda@tatimcomidinhas.com.br', 'Nanda (Fernanda Keller Garcia)', 'operação')
on conflict (email) do nothing;
