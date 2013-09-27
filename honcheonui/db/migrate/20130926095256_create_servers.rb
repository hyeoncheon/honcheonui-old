class CreateServers < ActiveRecord::Migration
  def change
    create_table :servers do |t|
      t.string :name
      t.string :status
      t.text :desc
      t.string :uuid
      t.string :os_name
      t.string :os_rel
      t.string :os_id
      t.string :os_kernel
      t.string :os_build
      t.string :os_arch
      t.string :op_mode
      t.string :op_level
      t.integer :st_uptime

      t.timestamps
    end
  end
end

### field information:
# name		hostname, uname -n (eg. silver)
# status	status of machine. (eg. ufo/...)
# desc		user's description
# uuid		server's uuid
#
# os_name	kernel name, uname -s (eg. Linux)
# os_rel	distribution rel, lsb_release -r (eg. Ubuntu)
# os_id		distribution id, lsb_release -i (eg. 12.04)
# os_kernel	kernel release, uname -r (eg. 3.5.0-40-generic)
# os_build	kernel build, uname -v (eg. #62...)
# os_arch	kernel arch, uname -m (eg. x86_64)
#
# op_mode	operation mode is deployed or not. (eg. dev/prod/...)
# op_level	operation level is similar to service level.
#
# st_uptime	status uptime is same as unix uptime.
