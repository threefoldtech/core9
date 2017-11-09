function $funcname(query)
    local obj = model_capnp_$name.$Name.parse(data) --deserialze capnp
    res={}
    return res
end

box.schema.func.create('$funcname', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

