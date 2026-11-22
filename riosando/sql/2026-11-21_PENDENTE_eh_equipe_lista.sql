-- ⚠️ PENDENTE — aplicado pelo publicar_admin.sh (etapa 1). Altera função EXISTENTE (ok do Eduardo em 21/11).
-- Efeito: quem está ATIVO na tabela `equipe` E tem e-mail VERIFICADO no Firebase passa a ver tudo que a equipe vê
-- (pedidos, cupons, afiliados, reservas, clientes…). A allowlist fixa não exige verificação (igual a hoje).
-- Pré-requisito: public.email_verificado() (2026-11-21_equipe_email_verificado.sql). Par: deploy do rio-api (rio-api_equipe_lista.diff).
-- Desfazer: 09_ROLLBACK_eh_equipe_lista.sql
create or replace function public.eh_equipe() returns boolean
  language sql stable security definer set search_path = public, auth as $$
  select coalesce(auth.email(),'') in ('riosandolito@gmail.com','eduardo.sumi@gmail.com')
      or (coalesce(auth.jwt() ->> 'email_verified', 'false') = 'true'
          and exists (select 1 from public.equipe e where e.email = lower(coalesce(auth.email(),'')) and e.ativo))
$$;
notify pgrst, 'reload schema';
