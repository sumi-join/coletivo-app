-- Painel 🍱 Cardápio: equipe logada liga/desliga produto e muda preço. Cliente logado NÃO.
-- Rodar como postgres (dono da tabela).
alter table produtos enable row level security;
drop policy if exists produtos_ler on produtos;
create policy produtos_ler on produtos for select using (true);
drop policy if exists produtos_equipe_edita on produtos;
create policy produtos_equipe_edita on produtos for update to authenticated using (eh_equipe()) with check (eh_equipe());
grant update (ativo, preco) on produtos to authenticated;
drop policy if exists produtos_servico on produtos;
create policy produtos_servico on produtos for all to service_role using (true) with check (true);
