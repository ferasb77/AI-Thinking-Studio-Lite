create or replace function public.handle_user_invited()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
    update public.user_security_state
    set must_change_password = false
    where user_id = new.id
      and must_change_password = true
      and password_changed_at is null;

    return new;
end;
$$;

revoke all on function public.handle_user_invited() from public;
revoke all on function public.handle_user_invited() from anon;
revoke all on function public.handle_user_invited() from authenticated;

drop trigger if exists mark_user_security_state_invited on auth.users;

create trigger mark_user_security_state_invited
after update of invited_at on auth.users
for each row
when (old.invited_at is null and new.invited_at is not null)
execute function public.handle_user_invited();

update public.user_security_state as security_state
set must_change_password = false
from auth.users as auth_user
where auth_user.id = security_state.user_id
  and auth_user.invited_at is not null
  and security_state.must_change_password = true
  and security_state.password_changed_at is null;