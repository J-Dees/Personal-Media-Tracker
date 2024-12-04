
--Books Table
create table
  public.books (
    id bigint generated by default as identity not null,
    book_title text not null,
    author text not null,
    constraint books_pkey primary key (id)
  ) tablespace pg_default;
--Games Table
create table
  public.games (
    id bigint generated by default as identity not null,
    game_title text not null,
    year bigint not null,
    constraint games_pkey primary key (id)
  ) tablespace pg_default;
--Movies Table
create table
  public.movies (
    id bigint generated by default as identity not null,
    movie_title text not null,
    year bigint not null,
    constraint movies_pkey primary key (id)
  ) tablespace pg_default;
  --Users Table
create table
  public.users (
    id bigint generated by default as identity not null,
    name text not null,
    constraint user_pkey primary key (id),
    constraint users_name_key unique (name)
  ) tablespace pg_default;
--Catalogs Table
create table
  public.catalogs (
    id bigint generated by default as identity not null,
    user_id bigint not null,
    name text not null,
    type public.entry_types not null,
    private boolean not null default false,
    constraint catalogs_pkey primary key (id),
    constraint user_catalog_name unique (user_id, name),
    constraint catalogs_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
  ) tablespace pg_default;
--All Entries Table
create table
  public.entries (
    id bigint generated by default as identity not null,
    catalog_id bigint not null,
    private boolean not null default false,
    recommend boolean null,
    date_created timestamp with time zone not null default now(),
    constraint entries_pkey primary key (id),
    constraint entries_catalog_id_fkey foreign key (catalog_id) references catalogs (id) on update cascade on delete cascade
  ) tablespace pg_default;
--Book Entries Table
create table
  public.book_entry (
    entry_id bigint generated by default as identity not null,
    book_id bigint not null,
    date_read date null,
    opinion text null,
    rating real null,
    read_again boolean null,
    constraint book_entry_pkey primary key (entry_id),
    constraint book_entry_book_id_fkey foreign key (book_id) references books (id) on update cascade on delete cascade,
    constraint book_entry_entry_id_fkey foreign key (entry_id) references entries (id) on update cascade on delete cascade,
    constraint rating_check check (
      (rating >= 0::double precision) and
      (rating <= 10::double precision)
    )
  ) tablespace pg_default;
--Game Entries Table
create table
  public.game_entry (
    entry_id bigint generated by default as identity not null,
    game_id bigint not null,
    hours_played real null,
    opinion text null,
    rating real null,
    play_again boolean null,
    constraint game_entry_pkey primary key (entry_id),
    constraint game_entry_entry_id_fkey foreign key (entry_id) references entries (id) on update cascade on delete cascade,
    constraint game_entry_game_id_fkey foreign key (game_id) references games (id) on update cascade on delete cascade,
    constraint rating_check check (
      (rating >= 0::double precision) and
      (rating <= 10::double precision)
    )
  ) tablespace pg_default;
--Movie Entries Table
create table
  public.movie_entry (
    entry_id bigint generated by default as identity not null,
    movie_id bigint not null,
    date_seen date null,
    opinion text null,
    rating real null,
    watch_again boolean null,
    constraint movie_entry_pkey primary key (entry_id),
    constraint movie_entry_entry_id_fkey foreign key (entry_id) references entries (id) on update cascade on delete cascade,
    constraint movie_entry_movie_id_fkey foreign key (movie_id) references movies (id) on update cascade on delete cascade,
    constraint rating_check check (
      (rating >= 0::double precision) and
      (rating <= 10::double precision)
    )
  ) tablespace pg_default;
--Other Entries Table
create table
  public.other_entry (
    entry_id bigint generated by default as identity not null,
    title text not null,
    description text null,
    price numeric null,
    quality text null,
    date_obtained date null,
    constraint other_entry_pkey primary key (entry_id),
    constraint other_entry_entry_id_fkey foreign key (entry_id) references entries (id) on update cascade on delete cascade
  ) tablespace pg_default;
--Social Table for follows.
create table
  public.social (
    user_id bigint not null,
    following_id bigint not null,
    constraint social_pkey primary key (user_id, following_id),
    constraint social_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade,
    constraint social_following_id_fkey foreign key (following_id) references users (id) on update cascade on delete cascade
  ) tablespace pg_default;

-------------------------------------- Verification Functions --------------------------------------
create function check_catalog_user_relationship(user_id INT, catalog_name TEXT, catalog_type entry_types)
returns boolean as $$
declare
  result bool := FALSE;
begin

  -- Check for user_id -> catalog pairing with a given catalog type
  select exists (
    select 1 from catalogs
    where
      catalogs.user_id = $1 and
      catalogs.name = catalog_name and
      catalogs.type = catalog_type
  ) into result;
  
  return result;
end;
$$ language plpgsql;

create function check_game_entry_exists(entry_name TEXT, entry_year INT)
returns boolean as $$
declare
  result bool := false;
begin
  select exists (
    select 1
    from games
    where
      games.game_title = entry_name and
      games.year = entry_year
  ) into result;
  return result;
end;
$$ language plpgsql;

create function check_movie_entry_exists(entry_name TEXT, entry_year INT)
returns boolean as $$
declare
  result bool := false;
begin
  select exists (
    select 1
    from movies
    where
      movies.movie_title = entry_name and
      movies.year = entry_year
  ) into result;
  return result;
end;
$$ language plpgsql;

create function check_book_entry_exists(entry_name TEXT, entry_author TEXT)
returns boolean as $$
declare
  result bool := false;
begin
  select exists (
    select 1
    from books
    where
      books.book_title = entry_name and
      books.author = entry_author
  ) into result;
  return result;
end;
$$ language plpgsql;

create function check_entry_in_catalog(user_id INT, catalog_name TEXT, catalog_type entry_types, entry_name TEXT)
returns boolean as $$
declare
  result bool := false;
begin
  
  -- Find entry given catalog information for each catalog_type
  case catalog_type
    when 'games' then
      select exists (
        select 1 from
        catalogs
        join 
          entries on catalogs.id = entries.catalog_id
        join 
          game_entry as ge on entries.id = ge.entry_id
        join 
          games on games.id = ge.game_id
        where 
          catalogs.user_id = $1 and
          catalogs.name = catalog_name and
          games.game_title = entry_name
      ) into result;
    when 'movies' then
      select exists (
        select 1 from
        catalogs
        join 
          entries on catalogs.id = entries.catalog_id
        join 
          movie_entry as me on entries.id = me.entry_id
        join 
          movies on movies.id = me.movie_id
        where 
          catalogs.user_id = $1 and
          catalogs.name = catalog_name and
          movies.movie_title = entry_name
      ) into result;
    when 'books' then
      select exists (
        select 1 from
        catalogs
        join 
          entries on catalogs.id = entries.catalog_id
        join 
          book_entry as be on entries.id = be.entry_id
        join 
          books on books.id = be.book_id
        where 
          catalogs.user_id = $1 and
          catalogs.name = catalog_name and
          books.book_title = entry_name
      ) into result;
    
    when 'other' then
      select exists (
        select 1 from catalogs
        join
          entries on catalogs.id = entries.catalog_id
        join
          other_entry as oe on entries.id = oe.entry_id
        where
          catalogs.user_id = $1 and
          catalogs.name = catalog_name and
          oe.title = entry_name
      ) into result;
    end case;
  return result;
end;
$$ language plpgsql;

create function check_rating_bounds(rating REAL)
returns boolean as $$
begin
return rating >= 0 and rating <= 10;
end;
$$ language plpgsql;
