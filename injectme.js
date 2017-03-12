addNumbers();

function addNumbers()
{
    var no = 1;

    var links = document.getElementsByTagName("a");
    for(var i=0;i<links.length;i++)
    {
        if(links[i].href)
        {
            links[i].innerHTML = links[i].innerHTML + " [" + no + "]";
            links[i].setAttribute("ml_link",no)
            no++;
        }
    }

    var links = document.getElementsByTagName("input");
        for(var i=0;i<links.length;i++)
        {
            if(links[i].value)
            {
                links[i].value = links[i].value + " [" + no + "]";
                links[i].setAttribute("ml_input",no)
                no++;
            }
            else
            {
                links[i].placeholder = " [" + no + "]";
                links[i].setAttribute("ml_input",no)
                no++;
            }
    }
}
