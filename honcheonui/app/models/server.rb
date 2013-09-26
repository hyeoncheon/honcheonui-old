class Server < ActiveRecord::Base
  attr_accessible :desc, :name, :op_level, :op_mode, :os_arch, :os_build, :os_id, :os_kernel, :os_name, :os_rel, :st_uptime, :status, :uuid
end
