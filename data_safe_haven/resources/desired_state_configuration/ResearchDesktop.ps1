Configuration ResearchDesktop {
    Import-DscResource -ModuleName nx

    Node localhost {
        nxScript EnsureMounts {
            GetScript = "
            #!/bin/bash
            ls -alh /data
            "
            SetScript = "
            #!/bin/bash
            ls -alh /data
            "
            TestScript = "
            #!/bin/bash
            exit 0
            "
        }
    }
}
