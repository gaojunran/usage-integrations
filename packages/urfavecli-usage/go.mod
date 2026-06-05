module github.com/gaojunran/usage-integrations/packages/urfavecli-usage

go 1.26.4

require (
	github.com/gaojunran/usage-integrations/packages/usage-spec-go v0.0.0-00010101000000-000000000000
	github.com/stretchr/testify v1.11.1
	github.com/urfave/cli/v2 v2.27.7
)

require (
	github.com/calico32/kdl-go v0.14.1 // indirect
	github.com/cpuguy83/go-md2man/v2 v2.0.7 // indirect
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/pmezard/go-difflib v1.0.0 // indirect
	github.com/russross/blackfriday/v2 v2.1.0 // indirect
	github.com/xrash/smetrics v0.0.0-20240521201337-686a1a2994c1 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

replace github.com/gaojunran/usage-integrations/packages/usage-spec-go => ../usage-spec-go
