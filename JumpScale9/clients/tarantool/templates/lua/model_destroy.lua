function $funcname()
    box.space.$name:truncate()
end
box.schema.func.create('$funcname', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

