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
