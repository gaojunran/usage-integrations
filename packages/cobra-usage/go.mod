module github.com/gaojunran/usage-integrations/packages/cobra-usage

go 1.26.4

replace github.com/gaojunran/usage-integrations/packages/usage-spec-go => ../usage-spec-go

require (
	github.com/gaojunran/usage-integrations/packages/usage-spec-go v0.0.0-00010101000000-000000000000
	github.com/spf13/cobra v1.10.2
	github.com/spf13/pflag v1.0.10
	github.com/stretchr/testify v1.11.1
)

require (
	github.com/calico32/kdl-go v0.14.1 // indirect
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/pmezard/go-difflib v1.0.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)
