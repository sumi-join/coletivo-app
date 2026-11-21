-- ⚠️ PENDENTE — NÃO APLICADO. Precisa do ok do Eduardo (altera função EXISTENTE).
-- Efeito: quem está ATIVO na tabela `equipe` passa a ver TUDO que a equipe vê no painel
-- (pedidos, cupons, afiliados, reservas, clientes…), não só as abas de loja/cardápio.
-- Com a tabela só com riosandolito + eduardo.sumi, o comportamento é idêntico ao de hoje.
-- Par obrigatório: deploy do rio-api com o diff rio-api_equipe_lista.diff (pedido manual, entregas, lançamentos).
-- Desfazer: rodar de novo a versão antiga (abaixo, comentada).
create or replace function public.eh_equipe() returns boolean
  language sql stable security definer set search_path = public, auth as $$
  select coalesce(auth.email(),'') in ('riosandolito@gmail.com','eduardo.sumi@gmail.com')
      or exists (select 1 from public.equipe e where e.email = lower(coalesce(auth.email(),'')) and e.ativo)
$$;
notify pgrst, 'reload schema';
-- versão antiga (21/11/2026):
-- create or replace function public.eh_equipe() returns boolean language sql stable security definer
--   set search_path = public, auth as $$ select coalesce(auth.email(),'') in ('riosandolito@gmail.com','eduardo.sumi@gmail.com') $$;
