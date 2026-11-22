-- Correção de segurança (21/11/2026): a tabela `equipe` só vale para e-mail VERIFICADO pelo Firebase.
-- Brecha: o app aceita cadastro por e-mail+senha sem verificar o e-mail; quem criasse conta com o e-mail da Nanda virava equipe.
-- O JWT chega ao Postgres em auth.jwt() (= current_setting('request.jwt.claims')); o claim email_verified é gravado pelo rio-api novo.
-- Só substitui funções criadas hoje (eh_equipe2, meu_acesso). A allowlist fixa antiga (eh_equipe) não muda aqui.
begin;
create or replace function public.email_verificado() returns boolean
  language sql stable set search_path = public, auth as $$
  select coalesce(auth.jwt() ->> 'email_verified', 'false') = 'true'
$$;
create or replace function public.eh_equipe2() returns boolean
  language sql stable security definer set search_path = public, auth as $$
  select public.eh_equipe()
      or (public.email_verificado()
          and exists (select 1 from public.equipe e
                       where e.email = lower(coalesce(auth.email(), '')) and e.ativo))
$$;
create or replace function public.meu_acesso() returns json
  language sql stable security definer set search_path = public, auth as $$
  select json_build_object(
    'email', auth.email(),
    'verificado', public.email_verificado(),
    'na_lista', exists (select 1 from public.equipe where email = lower(coalesce(auth.email(), '')) and ativo),
    'lista', public.eh_equipe2(),
    'completo', public.eh_equipe(),
    'nome', (select nome from public.equipe where email = lower(coalesce(auth.email(), ''))))
$$;
grant execute on function public.email_verificado(), public.eh_equipe2(), public.meu_acesso() to authenticated;
commit;
notify pgrst, 'reload schema';
