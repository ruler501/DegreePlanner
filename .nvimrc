function RunProg()
	let l:filename = expand('%')
	execute "!python3 " . l:filename . " http://catalog.utdallas.edu/now/undergraduate/programs/nsm/mathematics http://catalog.utdallas.edu/now/undergraduate/programs/ecs/computer-science http://catalog.utdallas.edu/now/undergraduate/programs/jsom/business-administration > scraped.out"
endfunction

function RunProgNoArg()
	let l:filename = expand('%')
	execute "!python3 " . l:filename . " > scraped.out"
endfunction

nnoremap <F2> :call RunProg()<CR>
nnoremap <F4> :call RunProgNoArg()<CR>
