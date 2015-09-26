function RunProg()
	let l:filename = expand('%')
	execute "!python3 " . l:filename . " > scraped.out"
endfunction

nnoremap <F2> :call RunProg()<CR>
