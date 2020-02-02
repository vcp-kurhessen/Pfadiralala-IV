-- Copyright (C) 2018 Kevin W. Hamlen
--
-- This program is free software; you can redistribute it and/or
-- modify it under the terms of the GNU General Public License
-- as published by the Free Software Foundation; either version 2
-- of the License, or (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA  02110-1301, USA.
--
-- The latest version of this program can be obtained from
-- http://songs.sourceforge.net.


VERSION = "3.1"
BIBLEDEFAULT = "bible.can"

-- fileopen(<filename>)
--   Open <filename> for reading, returning a filestate table on success or
--   nil on failure.
function fileopen(fnam)
  local handle
  if fnam ~= "-" then
    local msg,errno
    handle,msg,errno = io.open(fnam, "r")
    if not handle then
      io.stderr:write("songidx: Unable to open ",fnam," for reading.\n",
        "Error ",errno,": ",msg,"\n")
      return nil
    end
  else
    handle = io.stdin
    fnam = "stdin"
  end
  return { f=handle, filename=fnam, lineno=0 }
end

-- filereadln(<fstate>)
--   Read a line of input, returning the string or nil if at file-end.
function filereadln(fs)
  fs["lineno"] = fs["lineno"] + 1
  local s = fs["f"]:read()
  if not s then return nil end
  return s
end

-- closeout(<handle>)
--   Close an output file <handle>.
function closeout(handle)
  if handle == io.stdout then handle:flush()
  else handle:close() end
end

-- errorout(<handle>)
--   Respond to a write failure to <handle>.
function errorout(handle)
  closeout(handle)
  io.stderr:write("songidx: Error writing to output file. Aborting.\n")
    return 2
  end

-- fileclose(<fstate>)
--   Close file table <fstate>.
function fileclose(fs)
  if (fs["f"] ~= io.stdin) then fs["f"]:close() end
  fs["f"] = nil
  fs["filename"] = nil
  fs["lineno"] = 0
end

-- numprefix(<string>)
--   Find the longest prefix of <string> that represents a number (according to
--   the current locale) and contains no whitespace.  Return the number and the
--   suffix of <string> not parsed.  If there is no such prefix, return false
--   and the original <string>.
function numprefix(s)
  local _, len = unicode.utf8.find(s,"^%S*")
  for i=len, 1, -1 do
    local n = tonumber(s:sub(1,i))
    if n then return n, s:sub(i+1) end
  end
  return false, s
end

-- cleantitle(<song>)
--   Remove macros and braces from <song>'s title, and convert it to uppercase.
--   Macro-spaces ("\ ") are converted to regular spaces (" ").  Cache the
--   result to avoid re-cleaning during sorting.
function cleantitle(s)
  if not s["clean"] then
    local t = s["title"]:gsub("\\[^%a%s]","")
                        :gsub("\\(%s)","%1")
                        :gsub("\\%a+%s*","")
                        :gsub("{%s*","")
                        :gsub("}","")
    s["clean"] = unicode.utf8.upper(t)
  end
  return s["clean"]
end

-- songcmp(<song1>,<song2>)
--   Return true if <song1> is less than <song2>, and false otherwise.  The
--   ordering is first by title, then by index.  This function is suitable for
--   use with table.sort().
function songcmp(s1,s2)
  local t1 = cleantitle(s1)
  local t2 = cleantitle(s2)

  while true do
    -- Find the next word or number in each string.
    t1, t2 = unicode.utf8.match(t1,"%w.*"), unicode.utf8.match(t2,"%w.*")

    -- If there is no next word/number in both, sort by index.  If there is
    -- no next word/number in one but not the other, sort the shorter string
    -- before the longer one.
    if not t1 then
      if not t2 then break end
      return true
    elseif not t2 then return false end

    -- If one is a number, sort the number before the word.  If both are
    -- numbers (and are not equal), then sort in numerical order.
    local n1, n2
    n1, t1 = numprefix(t1)
    n2, t2 = numprefix(t2)
    if n1 then
      if not n2 or n1 < n2 then return true end
      if n1 > n2 then return false end
    elseif n2 then return false
    else
      -- Otherwise, both are words.  Lexicographically compare the words
      -- according to the current locale's collation conventions.  If the
      -- locale considers them "equal" (i.e., w1<w2 is false but w1<=w2 is true)
      -- then continue the loop to consider the next pair of words.
      local w1, w2 = unicode.utf8.match(t1,"^[%a'`]*"),
                     unicode.utf8.match(t2,"^[%a'`]*")
      local diff = w1 < w2
      if diff or not (w1 <= w2) then return diff end
      t1, t2 = t1:sub(#w1+1), t2:sub(#w2+1)
    end
  end

  -- If all corresponding words/numbers are equal, then sort alternate-form
  -- entries (e.g., lyrics) after normal entries (e.g., titles)
  local alt1, alt2 = s1["title"]:sub(1,1), s2["title"]:sub(1,1)
  if alt1 == "*" and alt2 ~= "*" then return false end
  if alt1 ~= "*" and alt2 == "*" then return true end

  -- If everything is the same, sort by the right-hand sides of the index
  -- entries (e.g., the song or page numbers).
  return s1["idx"] < s2["idx"]
end

-- setstartchars(<array>)
--   Try to find canonical "start characters" for each block of songs in a
--   sorted <array> of songs.  Since Lua doesn't currently have any means of
--   imparting a locale's alphabet, we adopt the following strategy:  Extract
--   the first unicode character from each title in the sorted list of titles
--   until reaching one that the locale's collation algorithm says is "bigger"
--   than the last.  Find the "smallest" first character in that set using
--   NON-UNICODE lexicographic sort.  This tends to be the most canonical one,
--   since unicode tends to put canonical (e.g., no-accent) glyphs at lower
--   code points than non-canonical (e.g., accented) ones.  (Unfortunately, if
--   none of the titles in the block start with the desired canonical glyph,
--   there's no way to guess it; we just use the best one available.)
function setstartchars(songs)
  local start = 1
  local best

  for i=1, #songs do
    local c = unicode.utf8.match(cleantitle(songs[i]),"%w")
    if c then
      c = unicode.utf8.upper(c)
      if not best then
        songs[start]["newblk"], start, best = "\\#", i, c
      elseif best < c then
        songs[start]["newblk"], start, best = best, i, c
      elseif #c < #best then best = c
      elseif #c == #best then
        for j=1,#c do
          if c:byte(j) < best:byte(j) then best = c; break
          elseif c:byte(j) > best:byte(j) then break end
        end
      end
    elseif best then
      songs[start]["newblk"], start, best = best, i, nil
    end
  end

  if start <= #songs then
    if best then
      songs[start]["newblk"] = best
    else
      songs[start]["newblk"] = "\\#"
    end
  end
end

wt_prefix = { A=true, THE=true }
wt_and = { AND=true }
wt_by = { BY=true }
wt_unknown = { UNKNOWN=true }

-- rotate(<title>)
--   If the first word of <title> is any word in wt_prefix, then shift that word
--   to the end of the string, preceded by a comma and a space.  So for example,
--   if wt_prefix contains "The", then rotate("The title") returns "Title, The".
--   Words in wt_prefix are matched case-insensitively, and the new first word
--   becomes capitalized.  If <title> begins with the marker character '*',
--   that character is ignored and left unchanged.
function rotate(s)
  local t = unicode.utf8.upper(s)
  local n = 0
  if s:sub(1,1) == "*" then n = 1 end
  for pre in pairs(wt_prefix) do
    if t:sub(1+n,n+#pre) == pre and
       unicode.utf8.find(t, "^%s+%S", n+#pre+1) then
      local len = unicode.utf8.len(pre)
      local x, y, z = unicode.utf8.match(unicode.utf8.sub(s,n+len+1),"^%s+(%W*)(%w?)(.*)$")
      return s:sub(1,n) .. x .. unicode.utf8.upper(y) .. z:gsub("\\%s","%0\1"):match("^(.-)%s*$"):gsub("\1","") .. ",~" .. unicode.utf8.sub(s,1+n,n+len)
    end
  end
  return s
end

-- matchany(<string>,<init>,<wordtable>)
--   If a word in <wordtable> case-insensitively matches to <string> starting
--   at index <init>, and if the match concludes with whitespace, then return
--   the index of the whitespace; otherwise return <init>.
function matchany(s,init,wt)
  local t = s:sub(init)
  local u = unicode.utf8.upper(t)
  for w,_ in pairs(wt) do
    if u:sub(1,#w) == w and
       (#w == #u or unicode.utf8.find(u, "^%s", #w+1)) then
      return init + #(unicode.utf8.sub(t,1,unicode.utf8.len(w)))
    end
  end
  return init
end

-- issuffix(<string>,<init>)
--   Return true if the abbreviation "Jr" or a roman numeral (followed by
--   nothing, space, period, comma, or semicolon) appears at position <init>
--   within <string>.  Return false otherwise.
function issuffix(s,i)
  return unicode.utf8.find(s, "^Jr$", i) or
         unicode.utf8.find(s, "^Jr[%s,;%.]", i) or
         unicode.utf8.find(s, "^[IVX]+$", i) or
         unicode.utf8.find(s, "^[IVX]+[%s,;%.]", i)
end

-- grabauthor(<string>)
--   Return a string of the form "Sirname, Restofname" denoting the full name
--   of the first author found in <string>; or return nil if no author name
--   can be found.  Also return an index to the suffix of <string> that was
--   not parsed, and just the "Sirname" part as a stand-alone string.
--
--   Precondition:  Caller must first sanitize <string> as follows:
--     <string>:gsub("[\1\2\3]","")
--             :gsub("\\\\","\\\1"):gsub("\\{","\\\2"):gsub("\\}","\\\3")
--
--   Postcondition: Caller must then unsanitize the returned <string> with:
--     <string>:gsub("\1","\\"):gsub("\2","{"):gsub("\3","}")
--
--   This is to allow grabauthor() to safely use Lua's %b pattern to find
--   balanced brace pairs without getting confused by escaped braces.
--
--   Heuristics:
--     * Names are separated by punctuation (other than hyphens, periods,
--       apostrophes, or backslashes) or by the word "and" (or whatever words
--       are in wt_and).
--       Special case: If a comma is followed by the abbreviation "Jr" or by a
--       roman numeral, then the comma does NOT end the author's name.
--     * If a name contains the word "by" (or anything in wt_by), then
--       everything before it is not considered part of the name.  (Let's hope
--       nobody is named "By".)
--     * The author's last name is always the last capitalized word in the
--       name unless the last capitalized word is "Jr." or a roman numeral.
--       In that case the author's last name is the penultimate captialized
--       word.
--     * If an author appears to have only a first name, or if the last name
--       found according to the above heuristics is an abbreviation (ending in
--       a period), look ahead in <string> until we find someone with a last
--       name and use that one.  This allows us to identify the first author in
--       a string like "Joe, Billy E., and Bob Smith" to be "Joe Smith".
--     * If the resultant name contains the word "unknown" (or any word in
--       wt_unknown), it's probably not a real name.  Recursively attempt
--       to parse the next author.
function grabauthor(authline,i)
  i = unicode.utf8.find(authline, "[^%s,;]", i)
  if not i then return nil end
  i = unicode.utf8.find(authline, "%S", matchany(authline,i,wt_and))
  if not i then return nil end
  i = unicode.utf8.find(authline, "%S", matchany(authline,i,wt_by))
  if not i then return nil end
  local skip = (matchany(authline,i,wt_unknown) > i)

  -- Set "first" to the index of the start of the first name, "last" to the
  -- index of the start of the sirname, "suffix" to the index of any suffix
  -- like "Jr." or "III" (or nil if there is none), and i to the index of the
  -- first character beyond the end of this author's name.
  local first,last,suffix = i,nil,nil
  while i <= #authline do
    while true do
      local j = select(2,authline:find("^\\%A", i)) or
                select(2,authline:find("^\\%a+%s*", i)) or
                select(2,authline:find("^%b{}", i))
      if not j then break end
      i = j + 1
    end
    if i > #authline then break
    elseif authline:sub(i,i) == "," then
      local j = unicode.utf8.find(authline, "%S", i+1)
      if j and issuffix(authline,j) then i = i + 1
      else break end
    elseif authline:sub(i,i) == ";" then break
    elseif unicode.utf8.find(authline, "^%s", i) then
      i = unicode.utf8.find(authline, "%S", i)
      if not i then i = #authline + 1; break end
      if matchany(authline, i, wt_and) > i then break end
      skip = skip or (matchany(authline, i, wt_unknown) > i)
      local j = matchany(authline, i, wt_by)
      if j > i then
        j = unicode.utf8.find(authline, "%S", j)
        if not j then last = i; break end  -- last name of "By"?
        i,first,last,suffix = j,j,nil,nil
      elseif issuffix(authline,i) then
        suffix = i
      elseif unicode.utf8.find(authline:sub(i):gsub("\\%A",""):gsub("\\%a+%s*",""),"^[%s{}'`\"]*%u") then
        last,suffix = i,nil
      end
    else
      i = select(2, unicode.utf8.find(authline, ".", i)) + 1
    end
  end

  -- If an "unknown" word appeared, skip this entry and parse the next.
  if skip then return grabauthor(authline,i) end

  -- Find the sirname.
  local sirname, fullname
  if last then
    sirname = unicode.utf8.gsub(authline:sub(last,(suffix or i)-1),
                                "([^%s,;\\])[%s,;]+$", "%1")
  end
  if not sirname or unicode.utf8.find(sirname, "%a%.$") then
    -- Here's where it gets tough.  We either have a single-word name, or the
    -- last name ends in a "." which means maybe it's just a middle initial or
    -- other abbreviation.  We could be dealing with a line like, "Billy,
    -- Joe E., and Bob Smith", in which case we have to go searching for the
    -- real last name.  To handle this case, we will try a recursive call.
    local _,_,r = grabauthor(authline,i)
    if r or not sirname then
      fullname = unicode.utf8.gsub(authline:sub(first,i-1),
                                   "([^%s,;\\])[%s,;]+$", "%1")
      if r then return (r .. ", " .. fullname), i, r
      else return fullname, i, nil end
    end
  end

  -- Add the first name.
  fullname = sirname .. ", " ..
    unicode.utf8.gsub(authline:sub(first,(last or suffix or i)-1),
                      "([^%s,;\\])[%s,;]+$", "%1")

  -- Add the suffix, if any.
  if suffix then
    fullname = fullname .. " " ..
      unicode.utf8.gsub(authline:sub(suffix,i-1), "([^%s,;\\])[%s,;]+$", "%1")
  end

  return fullname, i, sirname
end

-- genindex(<fstate>,<outname>)
--   Reads a title (if <authorindex>=false) or author (if <authorindex>=true)
--   index data file from file table <fstate> and generates a new file named
--   <outfile> containing a LaTeX title/author index.
--   Return Value: 0 on success, 1 on warnings, or 2 on failure
function genindex(fs,outname,authorindex)
  local songs = {}
  local seen = {}
  local wt = { wt_sep, wt_after, wt_prefix, wt_ignore }
  local typ = authorindex and "author" or "title"

  io.stderr:write("songidx: Parsing ",typ," index data file ",fs["filename"],"...\n")

  while true do
    local buf = filereadln(fs)
    if not buf then break end
    if buf:sub(1,1) == "%" then
      local j = buf:match("^()%%sep ") or
                buf:match("^%%()after ") or
                buf:match("^%%p()refix ") or
                buf:match("^%%ig()nore ")
      if j then
        if not seen[j] then
          for w in pairs(wt[j]) do wt[j][w] = nil end
          seen[j] = true
        end
        wt[j][unicode.utf8.upper(buf:sub(buf:find(" ")+1))] = true
      end
    else
      local snum = filereadln(fs)
      if not snum then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": incomplete song entry (orphan ",typ,")\n")
        return 2
      end
      local link = filereadln(fs)
      if not link then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": incomplete song entry (missing hyperlink)\n")
        return 2
      end
      if authorindex then
        local i,a = 1
        buf = buf:gsub("[\1\2\3]",""):gsub("\\\\","\\\1")
                 :gsub("\\{","\\\2"):gsub("\\}","\\\3")
        while true do
          a,i = grabauthor(buf, i)
          if not a then break end
          a = a:gsub("\1","\\"):gsub("\2","{"):gsub("\3","}")
          table.insert(songs, {title=a, num=snum, linkname=link, idx=#songs})
        end
      else
        buf = rotate(unicode.utf8.gsub(unicode.utf8.gsub(buf,"([^%s\\])%s+$","%1"),"^(%*?)%s+","%1"))
        table.insert(songs, {title=buf, num=snum, linkname=link, idx=#songs})
      end
    end
  end
  fileclose(fs)

  -- Sort the song table.
  table.sort(songs, songcmp)
  -- Find the index blocks.
  setstartchars(songs)

  -- Write the sorted data out to the output file.
  io.stderr:write("songidx: Generating ",typ," index TeX file ",outname,"...\n")
  local f,msg,errno
  if outname == "-" then
    f, outname = io.stdout, "stdout"
  else
    f,msg,errno = io.open(outname, "w")
    if not f then
      io.stderr:write("songidx: Unable to open ",outname," for writing.\n",
        "Error ",errno,": ",msg,"\n")
      return 2
    end
  end
  for i=1, #songs do
    if i>1 and songs[i]["title"] == songs[i-1]["title"] then
      if not f:write("\\\\\\songlink{",songs[i]["linkname"],"}{",songs[i]["num"],"}") then return errorout(f) end
    else
      if songs[i]["newblk"] then
        if i>1 then
          if not f:write("}\n\\end{idxblock}\n") then return errorout(f) end
        end
        if not f:write("\\begin{idxblock}{",songs[i]["newblk"]) then return errorout(f) end
      end
      if songs[i]["title"]:find("^%*") then
        if not f:write("}\n\\idxaltentry{",songs[i]["title"]:sub(2)) then return errorout(f) end
      else
        if not f:write("}\n\\idxentry{",songs[i]["title"]) then return errorout(f) end
      end
      if not f:write("}{\\songlink{",songs[i]["linkname"],"}{",songs[i]["num"],"}") then return errorout(f) end
    end
  end
  if #songs > 0 then
    if not f:write("}\n\\end{idxblock}\n") then return errorout(f) end
  end

  return 0
end

bible = {}
chapX = 0

-- readbible(<filename>)
--   Read bible data file <filename> into the bible table.  Return nil on error
--   or true on success.
function readbible(filename)
  local fs = fileopen(filename)
  if not fs then return nil end
  bible = {}

  while true do
    local buf = filereadln(fs)
    if not buf then break end
    if buf:sub(1,1) ~= "#" and buf:find("%S") then
      local t, vbuf = { name = buf:match("^[^|]*"),
                        aliases = "|" .. unicode.utf8.upper(buf) .. "|" }
      repeat
        vbuf = filereadln(fs)
        if not vbuf then
          io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": incomplete bible book entry (book title with no verses)\n")
          fileclose(fs)
          return nil
        end
      until vbuf:sub(1,1) ~= "#" and buf:find("%S")
      if vbuf:find("[^%d%s]") then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": verse count includes a non-digit\n")
        fileclose(fs)
        return nil
      end
      for n in vbuf:gmatch("%d+") do
        local i = tonumber(n)
        if not i then
          io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": invalid number ",n,"\n")
          fileclose(fs)
          return nil
        end
        i = math.floor(i)
        if chapX < i+1 then chapX = i+1 end
        table.insert(t, i)
      end
      table.insert(bible, t)
    end
  end

  fileclose(fs)
  return true
end

-- parseref(<string>,<init>,<book>,<chapter>)
--   Interpret the characters starting at index <init> of <string> as a
--   scripture reference, and return four values: (1) the index of the first
--   character after <init> not parsed, (2) the book number parsed, (3) the
--   chapter number parsed (or 1 if the book has only verses), and (4) the
--   verse number parsed.  Arguments <book> and <chapter> are the PREVIOUS book
--   number and chapter parsed, or -1 if none.  If book or chapter information
--   is missing from <string>, they will be drawn from <book> and <chapter>.
--   That way, successive calls can correctly parse a run-on string like
--   "Philippians 3:1,5; 4:3", infering that "5" refers to "Philippians 3" and
--   "4:3" refers to "Philippians".  If the parser encounters an error in
--   processing the book name (e.g., a book name was specified but not
--   recognized), then #bible+1 is returned for the book.  If no chapter or no
--   verse is provided (e.g., the reference is just "Philippians" or
--   "Philippians 3") then the chapter and/or verse are returned as -1.
function parseref(s,i,book,ch)
  local v = -1
  i = unicode.utf8.find(s,"%S",i)
  if not i then return nil end
  local j = unicode.utf8.find(s,"[%d:]*%s*[,;%-]",i) or
            unicode.utf8.find(s,"[%d:]*%s*$",i)
  local bookname = "|" .. unicode.utf8.upper(unicode.utf8.match(s:sub(i,j-1), "(.-)%s*$")) .. "|"
  i = j
  if bookname ~= "||" then
    book, ch = #bible+1, -1
    for b,t in pairs(bible) do
      if t["aliases"]:find(bookname, 1, true) then book = b; break end
    end
  end
  j = unicode.utf8.find(s,"%D",i) or (#s+1)
  if s:sub(j,j) == ":" then
    ch, i = (tonumber(s:sub(i,j-1)) or -1), j+1
    j = unicode.utf8.find(s,"%D",i) or (#s+1)
  end
  if ch<=0 and book>0 and #bible[book] == 1 then
    -- Special case: This book has only one chapter.
    ch = 1
  end
  if ch <= 0 then
    ch = tonumber(s:sub(i,j-1)) or -1
  else
    v = tonumber(s:sub(i,j-1)) or -1
  end
  i = unicode.utf8.find(s,"%S",j)
  if not i then i = #s+1
  elseif not s:find("^[,;%-]",i) then return nil end
  return i, book, ch, v
end

-- vlt(<chapter1>,<verse1>,<chapter2>,<verse2>)
--   Return true if <chapter1>:<verse1> precedes <chapter2>:<verse2> and false
--   otherwise.
function vlt(ch1,v1,ch2,v2)
  return ch1 < ch2 or (ch1 == ch2 and v1 < v2)
end

-- vinc(<book>,<chapter>,<verse>)
--   Return the chapter,verse pair of the verse immediately following
--   <chapter>:<verse> in <book>.  If <chapter>:<verse> is the last verse in
--   <book>, the returned chapter will not exist in <book>.
function vinc(book,ch,v)
  if v < bible[book][ch] then return ch, v+1 end
  return ch+1, 1
end

-- vdec(<book>,<chapter>,<verse>)
--   Return the chapter,verse pair of the verse immediately preceding
--   <chapter>:<verse> in <book>.  If <chapter> and <verse> are both 1,
--   then 0,nil will be returned.
function vdec(book,ch,v)
  if v > 1 then return ch, v-1 end
  return ch-1, bible[book][ch-1]
end

-- unpack_cv(<cv>)
--   Decompose a chapter-verse key (computed as cv*chapX+v) into the original
--   chapter and verse numbers.
function unpack_cv(cv)
  local v = cv % chapX
  return (cv-v)/chapX, v
end

-- eqdom(<table1>,<table2>)
--   Return true if two tables have identical domains; false otherwise.
function eqdom(t1,t2)
  for k,_ in pairs(t1) do if not t2[k] then return false end end
  for k,_ in pairs(t2) do if not t1[k] then return false end end
  return true
end

-- insertref(<is_add>,<changeset>,<chapter>,<verse>,<song>,<link>,<key>)
--   Insert song <song>,<link>,<key> into the set of "adds" (if <is_add>=true)
--   or "drops" (if <is_add>=false) for verse <chapter>:<verse> in <changeset>.
--   A <changeset> is a table that maps cv's to {adds=<refset>, drops=<refset>}
--   tables, where cv's are chapter-verse pairs encoded as chapter*chapX+verse.
--   Each such entry denotes a verse where the set of songs that reference it
--   changes.  The "adds" field lists the songs that refer to this verse but
--   not the previous one.  The "drops" field lists the songs that refer to
--   this verse but not the next.  This formulation allows us to efficiently
--   represent range-references (e.g., "Psalms 1:1-8") without creating a
--   separate table entry for each verse in the range.
--   Create a new entry for <chapter>:<verse> in <changeset> if it doesn't
--   already exist.  Return the new <changeset>.
function insertref(is_add,set,ch,v,n,l,k)
  if not set then set = {} end
  local cv = ch*chapX+v
  if not set[cv] then set[cv] = { adds={}, drops={} } end
  set[cv][is_add and "adds" or "drops"][k] = { num=n, link=l }
  return set
end

-- print_vrange(<file>,<book>,<ch1>,<v1>,<ch2>,<v2>,<lastchapter>)
--   Output LaTeX material to file <file> for verse range <ch1>:<v1>--<ch2>:<v2>
--   of book number <book>.  Depending on <lastchapter>, the outputted material
--   might be the start of a new index entry or the continuation of a previous
--   entry.  If <lastchapter> is positive, continue the previous entry and
--   print the chapter of <ch1>:<v1> only if it differs from <lastchapter>.  If
--   <lastchapter> is negative, continue the previous entry and always print
--   the chapter number of <ch1>:<v1>.
function print_vrange(f,b,ch1,v1,ch2,v2,lch)
  local r = f:write(lch == 0 and "\\idxentry{" or ",")
  
  if v1 <= 0 then
    if lch ~= 0 then r = r and f:write("\\thinspace ") end
    r = r and f:write(ch1)
  elseif 0 <= b and b < #bible and #bible[b] == 1 then
    -- This book has only one chapter.
    if lch ~= 0 then r = r and f:write("\\thinspace ") end
    r = r and f:write(v1)
  elseif lch <= 0 or lch ~= ch1 or ch1 ~= ch2 then
    if lch ~= 0 then r = r and f:write(" ") end
    r = r and f:write(ch1,":",v1)
  else
    if lch ~= 0 then r = r and f:write("\\thinspace ") end
    r = r and f:write(v1)
  end

  if vlt(ch1,v1,ch2,v2) then
    if v2 <= 0 then
      r = r and f:write("--",ch2)
    elseif ch1 ~= ch2 then
      r = r and f:write("--",ch2,":",v2)
    else
      r = r and f:write("--",v2)
    end
  end

  return r
end

-- print_reflist(<file>,<refset>)
--   Output the list of song references given by <refset> in sorted order
--   to file <file>.
function print_reflist(f,t)
  local r = true
  local s = {}
  for k,_ in pairs(t) do table.insert(s,k) end
  table.sort(s)

  local first = true
  for _,k in ipairs(s) do
    if first then first = false else r = r and f:write("\\\\") end
    r = r and f:write("\\songlink{",t[k]["link"],"}{",t[k]["num"],"}")
  end
  return r
end

function debug_print_reflist(r)
  local first = true
  io.stderr:write("{")
  for k,_ in pairs(r) do
    if first then first=false else io.stderr:write(",") end
    io.stderr:write(k)
  end
  io.stderr:write("}")
end

function debug_print_changeset(x)
  if not x then io.stderr:write("nil") else
    for cv,r in pairs(x) do
      local ch,v = unpack_cv(cv)
      io.stderr:write("{",ch,":",v," --> adds=")
      debug_print_reflist(r["adds"])
      io.stderr:write(", drops=")
      debug_print_reflist(r["drops"])
      io.stderr:write("}")
    end
  end
end

-- genscriptureindex(<fstate>,<outname>,<biblename>)
--   Generate a LaTeX file named <outname> containing material suitable to
--   typeset the scripture index data found in input file <fstate>.  Input
--   bible data from an ascii file named <biblename>.  Return 0 on success,
--   1 if there were warnings, and 2 if there was a fatal error.
function genscriptureindex(fs,outname,biblename)
  local hadwarnings = 0
  local idx = {}

  io.stderr:write("songidx: Parsing scripture index data file ",fs["filename"],"...\n")

  -- Read the bible data file into the bible array.
  if not readbible(biblename) then return 2 end

  -- Walk through the input file and construct a <changeset> for each book
  -- of the bible.  Each changeset represents the set of verses in that book
  -- referred to by songs in the song book.
  local key = 0
  while true do
    local ref = filereadln(fs)
    if not ref then break end
    local n = filereadln(fs)
    if not n then
      io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": incomplete song entry (orphan reference line)\n")
      fileclose(fs)
      return 2
    end
    local l = filereadln(fs)
    if not l then
      io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": incomplete song entry (missing hyperlink)\n")
      fileclose(fs)
      return 2
    end
    key = key + 1

    local i = 1
    local book, ch1, v1, ch2, v2 = -1, -1, -1, -1, -1
    while i <= #ref do
      i,book,ch1,v1 = parseref(ref,i,book,ch1)
      ch2,v2 = ch1,v1
      if not i then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Malformed scripture reference for song ",n,". Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if book < 1 then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," doesn't include a book name. Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if book > #bible then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," references unknown book. Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if ch1 < 1 then ch1 = 1 end
      if ch1 > #bible[book] then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," refers to ",bible[book]["name"]," ",ch1,", which doesn't exist. Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if v1 < 1 then v1 = 1 end
      if v1 > bible[book][ch1] then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," refers to ",bible[book]["name"]," ",ch1,":",v1,", which doesn't exist. Ignoring it.\n")
        hadwarnings = 1
        break
      end

      if ref:sub(i,i) == "-" then
        -- If the reference ends in a "-", it starts an explicit range.
        -- Parse the next reference to find the range's end.
        i = unicode.utf8.find(ref, "[^%s%-]", i)
        if not i then
          io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," has range with no limit. Ignoring it.\n")
          hadwarnings = 1
          break
        end
        local book2
        i,book2,ch2,v2 = parseref(ref,i,book,ch1)
        if not i then
          io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Malformed scripture reference for song ",n,". Ignoring it.\n")
          hadwarnings = 1
          break
        end
        if book2 ~= book then
          io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," appears to span books! Ignoring it.\n")
          hadwarnings = 1
          break
        end
      end
      if ch2 < 1 then ch2 = #bible[book] end
      if ch2 > #bible[book] then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," refers implicitly to ",bible[book]["name"]," ",ch2,", which doesn't exist. Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if v2 < 1 then v2 = bible[book][ch2]
      elseif v2 > bible[book][ch2] then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," refers implicitly to chapter ",ch2," of ",bible[book]["name"],", which doesn't exist. Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if vlt(ch2,v2,ch1,v1) then
        io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": WARNING: Scripture reference for song ",n," contains backwards range ",bible[book]["name"]," ",ch1,":",v1,"-",ch2,":",v2,". Ignoring it.\n")
        hadwarnings = 1
        break
      end
      if i < #ref then i = i + 1 end

      idx[book] = insertref(true, idx[book], ch1, v1, n, l, key)
      idx[book] = insertref(false, idx[book], ch2, v2, n, l, key)
    end
  end
  fileclose(fs)

  -- Now create the index .sbx file.
  io.stderr:write("songidx: Generating scripture index TeX file ",outname,"...\n")
  local f,msg,errno
  if outname == "-" then
    f, outname = io.stdout, "stdout"
  else
    f,msg,errno = io.open(outname, "w")
    if not f then
      io.stderr:write("songidx: Unable to open ",outname," for writing.\n",
        "Error ",errno,": ",msg,"\n")
      return 2
    end
  end

  -- For each book of the bible the has songs that reference it, go through its
  -- <changeset> and generate a sequence of index entries.  Wherever possible,
  -- compact adjacent entries that have identical <refset>'s so that we never
  -- have two consecutive index entries with identical right-hand sides.
  for b=1,#bible do
    local x = idx[b]
    if x then
      -- io.stderr:write("idx[",b,"] = ")
      -- debug_print_changeset(x)
      local s, t = {}, {}
      for cv,_ in pairs(x) do table.insert(s,cv) end
      table.sort(s)
      local lch = 0  -- 0=none, -1=force printing of chapter
      local cv1 = s[1]
      local ch1,v1 = unpack_cv(cv1)
      if not f:write("\\begin{idxblock}{",bible[b]["name"],"}\n") then return errorout(f) end
      for i,cv in ipairs(s) do
        local this = x[cv]
        local ch,v = unpack_cv(cv)
        local ncv,nxt,nch,nv = s[i+1]
        if ncv then
          nxt,nch,nv = x[ncv], unpack_cv(ncv)
        end
        for k,r in pairs(this["adds"]) do t[k] = r end
        local skip = false
        if ncv and eqdom(this["drops"], nxt["adds"]) then
          -- Set of drops here equals set of adds next time.  There's at least
          -- a chance that we can combine this item and the next one into a
          -- single index entry.
          local ch2, v2 = vinc(b,ch,v)
          if not vlt(ch2,v2, nch,nv) then
            -- If the next item is adjacent to this one, do nothing.  Just let
            -- the range in progress be extended.  We'll output a single entry
            -- for all of these adjacent verses when we reach the end.
            skip = true
          elseif eqdom(t, this["drops"]) then
            -- Otherwise, if the next item is not adjacent but all refs are
            -- dropped here, then print a partial entry to be continued with a
            -- comma next time.
            if not print_vrange(f,b,ch1,v1,ch,v,lch) then return errorout(f) end
            lch = (ch1 == ch) and ch or -1
            ch1, v1 = nch, nv
            skip = true
          end
        end
        if not skip then
          if next(this["drops"]) then
            -- Some songs get dropped here, and either the next item is not
            -- adjacent to this one, or it's adjacent and the set of adds is not
            -- the same.  In either case, that means the set of refs changes at
            -- this point, so we need to output a full entry (or finish the one
            -- in progress).
            if not (print_vrange(f,b,ch1,v1,ch,v,lch) and
                    f:write("}{") and
                    print_reflist(f,t) and
                    f:write("}\n")) then return errorout(f) end
            for k,_ in pairs(this["drops"]) do t[k] = nil end
            lch = 0
            if not next(t) and ncv then
              ch1, v1 = nch, nv
            else
              ch1, v1 = vinc(b,ch,v)
            end
          end
          if next(t) and ncv and next(nxt["adds"]) and vlt(ch1,v1,nch,nv) then
            -- There are verses between this item and the next which have refs,
            -- but the refs change at the beginning of the next item.  Make an
            -- entry for the intermediate block of verses.
            local ch2, v2 = vdec(b,nch,nv)
            if not (print_vrange(f,b,ch1,v1,ch2,v2,lch) and
                    f:write("}{") and
                    print_reflist(f,t) and
                    f:write("}\n")) then return errorout(f) end
            lch, ch1, v1 = 0, nch, nv
          end
        end
      end
      if not f:write("\\end{idxblock}\n") then return errorout(f) end
    end
  end

  closeout(f)
  return hadwarnings
end

-- Main program entry point
function main()
  local fs, biblename, inname, outname, locale

  local i = 1
  while arg[i] do
    if arg[i] == "-v" or arg[i] == "--version" then
      io.write("songidx ", VERSION, "\n",
        "Copyright (C) 2018 Kevin W. Hamlen\n",
        "License GPLv2: GNU GPL version 2 or later",
	      " <http://gnu.org/licenses/gpl.html>\n",
	      "This is free software: you are free to change and redistribute it.\n",
	      "There is NO WARRANTY, to the extent permitted by law.\n")
      return 0
    elseif arg[i] == "-h" or arg[i] == "--help" then
      io.write("Syntax: ",arg[-1]," ",arg[0]," [options] input.sxd [output.sbx]\n",
"Available options:\n",
"  -b FILE          Set the bible format when generating a scripture index\n",
"  --bible FILE      (default: ", BIBLEDEFAULT, ")\n",
"\n",
"  -l LOCALE        Override the default system locale (affecting how non-\n",
"  --locale LOCALE   English characters are sorted).  See your system help\n",
"                    for valid LOCALEs.\n",
"\n",
"  -h               Display this help file and stop.\n",
"  --help\n",
"\n",
"  -v               Print version information and stop.\n",
"  --version\n",
"\n",
"If omitted, [output.sbx] defaults to the input filename but with the file\n",
"extension renamed to '.sbx'. To read or write to stdin or stdout, use '-'\n",
"in place of input.sxd or output.sbx.\n",
"\n",
"See http://songs.sourceforge.net for support.\n")
      return 0
    elseif arg[i] == "-b" or arg[i] == "--bible" then
      if biblename then
        io.stderr:write("songidx: multiple bible files specified\n")
        return 2
      end
      i = i + 1
      if arg[i] then
        biblename = arg[i]
      else
        io.stderr:write("songidx: ",arg[i-1]," option requires an argument\n")
        return 2
      end
    elseif arg[i] == "-l" or arg[i] == "--locale" then
      if locale then
        io.stderr:write("songidx: multiple locales specified\n")
        return 2
      end
      i = i + 1
      if arg[i] then
        locale = arg[i]
      else
        io.stderr:write("songidx: ",arg[i-1]," requires an argument\n")
        return 2
      end
    elseif arg[i] == "-o" or arg[i] == "--output" then
      if outname then
        io.stderr:write("songidx: multiple output files specified\n")
        return 2
      end
      i = i + 1
      if arg[i] then
        outname = arg[i]
      else
        io.stderr:write("songidx: ",arg[i-1]," option requires an argument\n")
        return 2
      end
    elseif arg[i]:sub(1,1) == "-" and arg[i] ~= "-" then
      io.stderr:write("songidx: unknown option ",arg[i],"\n")
      return 2
    elseif not inname then inname = arg[i]
    elseif not outname then outname = arg[i]
    else
      io.stderr:write("songidx: too many command line arguments\n")
      return 2
    end
    i = i + 1
  end

  if not locale then
    os.setlocale("")
  elseif not os.setlocale(locale) then
    io.stderr:write("songidx: invalid locale: ",locale,"\n")
    return 2
  end

  if not inname then
    io.stderr:write("songidx: no input file specified\n")
    return 2
  end
  if not outname then
    if inname == "-" then
      outname = "-"
    else
      local n
      outname,n = inname:gsub("%.[^%./\\]*$", ".sbx")
      if n == 0 then outname = inname .. ".sbx" end
    end
  end
  if not biblename then biblename = BIBLEDEFAULT end

  fs = fileopen(inname)
  if not fs then return 2 end

  local retval = 2
  local buf = filereadln(fs)
  if not buf then
    io.stderr:write("songidx:",fs["filename"],": file is empty\n")
    fileclose(fs)
  elseif buf == "TITLE INDEX DATA FILE" then
    retval = genindex(fs,outname,false)
  elseif buf == "SCRIPTURE INDEX DATA FILE" then
    retval = genscriptureindex(fs,outname,biblename)
  elseif buf == "AUTHOR INDEX DATA FILE" then
    retval = genindex(fs,outname,true)
  else
    io.stderr:write("songidx:",fs["filename"],":",fs["lineno"],": file has unrecognized format\n")
    fileclose(fs)
  end

  if retval == 0 then
    io.stderr:write("songidx: Done!\n")
  elseif retval == 1 then
    io.stderr:write("songidx: COMPLETED WITH ERRORS. SEE ABOVE.\n")
  else
    io.stderr:write("songidx: FAILED. SEE ERROR MESSAGES ABOVE.\n")
  end

  return retval
end

os.exit(main())

